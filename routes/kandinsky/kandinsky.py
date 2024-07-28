import asyncio
from base64 import b64decode
import datetime
import json
import os

import aiohttp
from fastapi import APIRouter, Depends, HTTPException, status, Request
import requests
import typing as T

from pydantic import BaseModel, Field, model_validator
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session

from ..auth import login_request
from tools.limiter import limiter_ip
from tools.validation import is_valid_api_key
from infrastructure.databases import get_db_pg

from envparse import env

env.read_envfile()

router = APIRouter(prefix="/kandinsky", tags=["kandinsky"])
request_limiter = "2/second"


class Kandinsky:
    def __init__(self):
        self.url = env.str("KANDINSKY_API_URL")
        self._auth_headers = {
            "X-Key": f"Key {env.str('KANDINSKY_API_KEY')}",
            "X-Secret": f"Secret {env.str('KANDINSKY_API_SECRET')}",
        }
        self.model_id = self._get_model()

    def _get_model(self):
        response = requests.get(self.url + "/key/api/v1/models", headers=self._auth_headers)
        print(response.json())
        return response.json()[0]["id"]

    async def generate_image_async(
        self,
        session,
        prompt: str,
        width: int,
        height: int,
        style: str = None,
        use_beautificator: bool = False,
        negative_prompt: str = "",
        prior_num_interference_steps: int = 300,
        prior_guidance_scale: float = 6.0,
        num_interference_steps: int = 500,
        guidance_scale: float = 7.5,
    ) -> str:
        """Отправляет запрос на генерацию изображения и возвращает UUID запроса

        :param session: HTTPX сессия
        :param prompt: Текстовое описание изображения
        :param width: Ширина изображения
        :param height: Высота изображения
        :param style: Стиль изображения
        :param use_beautificator: Использовать фильтры улучшения изображения
        :param negative_prompt: Указание, что не должно быть на изображении
        :param prior_num_interference_steps: Количество шагов денойзинга
        :param prior_guidance_scale: Масштаб управления для более точного соответствия промпту
        :param num_interference_steps: Количество шагов денойзинга во время генерации изображения
        :param guidance_scale: Масштаб, способствующий созданию изображений, соответствующих промпту
        :return: UUID запроса
        """

        params = {
            "type": "GENERATE",
            "num_images": 1,
            "width": width,
            "height": height,
            "censor": {"useGigaBeautificator": use_beautificator},
            "generateParams": {"query": prompt},
            "negativePromptDecoder": negative_prompt,
            "prior_num_interference_steps": prior_num_interference_steps,
            "prior_guidance_scale": prior_guidance_scale,
            "num_interference_steps": num_interference_steps,
            "guidance_scale": guidance_scale,
        }

        if style:
            params["style"] = style

        data = aiohttp.FormData()
        data.add_field("model_id", str(self.model_id))
        data.add_field("params", json.dumps(params), content_type="application/json")

        response = await session.post(self.url + "/key/api/v1/text2image/run", headers=self._auth_headers, data=data)
        data = await response.json()
        return data["uuid"]

    async def check_generate_status(self, session, request_id: str) -> str | None:
        response = await session.get(
            self.url + f"/key/api/v1/text2image/status/{request_id}", headers=self._auth_headers
        )
        data = await response.json()
        if data["status"] == "DONE":
            return data["images"][0]
        return None


async def guidance_correction(width: int, height: int, prompt: str) -> float:
    # TODO document why this method is empty
    pass


kandinsky = Kandinsky()


class ImageSettingsModel(BaseModel):
    prompt: str
    negative_prompt: str = ""
    width: int = Field(..., ge=128, le=2942)
    height: int = Field(..., ge=128, le=2942)
    beautificator: bool = False
    style: T.Optional[str] = None
    images: int = 1

    @model_validator(mode="after")
    def dimension_validator(self):
        width = self.width
        height = self.height
        if width + height > 3070:
            raise ValueError("Сумма сторон не должна превышать 3070")
        return self


class ImagesResponseModel(BaseModel):
    images: list[str]


@router.post("/generate/image", response_model=ImagesResponseModel)
@limiter_ip.limit(request_limiter)
async def generate_kandinsky_image(request: Request, image_settings: ImageSettingsModel):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for _ in range(image_settings.images):
            tasks.append(
                kandinsky.generate_image_async(
                    session=session,
                    prompt=image_settings.prompt,
                    negative_prompt=image_settings.negative_prompt,
                    height=image_settings.height,
                    width=image_settings.width,
                    use_beautificator=image_settings.beautificator,
                    style=image_settings.style,
                )
            )

        request_ids = await asyncio.gather(*tasks)

        generated_images = []
        MAX_ATTEMPTS = 600
        for request_id in request_ids:
            while not (image := await kandinsky.check_generate_status(session, request_id)):
                MAX_ATTEMPTS -= 1
                print("Оставшееся кол-во попыток: " + str(MAX_ATTEMPTS))
                if MAX_ATTEMPTS <= 0:
                    return JSONResponse(status_code=500, content={"error": "Image generation failed."})
                await asyncio.sleep(1)

            generated_images.append(image)

    # Сохранение изображений
    # for i, image in enumerate(generated_images):
    #     image_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(i) + '.jpg'
    #     image_path = os.path.join('generated_images/' + image_name)
    #     with open(image_path, 'wb') as f:
    #         f.write(b64decode(image))

    return JSONResponse(status_code=200, content={"images": generated_images})

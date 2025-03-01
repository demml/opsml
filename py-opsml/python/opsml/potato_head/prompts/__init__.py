# type: ignore
# pylint: disable=no-name-in-module

from .. import potato_head

ChatPartImage = potato_head.prompts.ChatPartImage
ChatPrompt = potato_head.prompts.ChatPrompt
ChatPartText = potato_head.prompts.ChatPartText
ChatPartAudio = potato_head.prompts.ChatPartAudio
ImageUrl = potato_head.prompts.ImageUrl
Message = potato_head.prompts.Message
PromptType = potato_head.prompts.PromptType


__all__ = [
    "ChatPartImage",
    "ChatPartText",
    "ChatPrompt",
    "ChatPartAudio",
    "ImageUrl",
    "Message",
    "PromptType",
]

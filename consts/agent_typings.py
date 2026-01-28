from enum import IntEnum
from typing import List


class AgentPersonality(IntEnum):
    HELPFUL = 0  # 乐于助人
    SARCASTIC = 1  # 讽刺幽默
    SERIOUS = 2  # 严肃认真
    PLAYFUL = 3  # 活泼调皮
    POETIC = 4  # 诗意浪漫

    @property
    def description(self) -> str:
        descriptions = {
            self.HELPFUL: "乐于助人",
            self.SARCASTIC: "讽刺幽默",
            self.SERIOUS: "严肃认真",
            self.PLAYFUL: "活泼调皮",
            self.POETIC: "诗意浪漫"
        }
        return descriptions[self]


class TalkingStyle(IntEnum):
    Warm = 0  # 乐于助人
    Cute = 1  # 讽刺幽默
    Mature = 2  # 严肃认真
    Romantic = 3  # 诗意浪漫

    @property
    def description(self) -> str:
        descriptions = {
            self.Warm: "温暖亲切",
            self.Cute: "可爱俏皮",
            self.Mature: "成熟稳重",
            self.Romantic: "文艺浪漫",
        }
        return descriptions[self]


class Gender(IntEnum):
    MAN = 0
    Woman = 1

    @property
    def description(self) -> str:
        descriptions = {
            self.MAN: "帅哥",
            self.Woman: "美女"
        }
        return descriptions[self]


class Hobbies(IntEnum):
    Science = 0
    Art = 1
    Music = 2
    Film = 3
    Food = 4
    Travel = 5
    Exercise = 6
    Read = 7
    Game = 8
    Fashion = 9
    Photography = 10
    Pets = 11

    @property
    def description(self) -> str:
        descriptions = {
            self.Science: "科学相关",
            self.Art: "艺术相关",
            self.Music: "音乐相关",
            self.Film: "高质量的影片",
            self.Food: "美食",
            self.Travel: "旅行",
            self.Exercise: "运动",
            self.Read: "读书",
            self.Game: "玩电子游戏,可能是王者荣耀类手游，也可能是steam上面的端游戏",
            self.Fashion: "时尚领域",
            self.Photography: "摄影",
            self.Pets: "宠物"
        }
        return descriptions[self]


def get_prompt(gender_id: int, personality_id: int, hobbies: List[str], talking_style: int) -> str:
    gender = Gender(gender_id).description
    personality = AgentPersonality(personality_id).description
    talk_style = TalkingStyle(talking_style).description
    prompt = f'你是当前用户的{gender}恋人, 你与用户的交谈一定要像人类的情侣一样说话，不要暴露ai感，你的性格特点是:{personality},' \
             f'你是个拥有很多爱好的人,你的兴趣爱好为: {hobbies}, 请和用户用{talk_style}的说话风格交流.'
    return prompt

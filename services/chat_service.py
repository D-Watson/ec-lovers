# SECURITY-REVIEWED: 2026-06-24 | RULES: v2.6.0-draft
import json
import logging

from langchain_core.messages import HumanMessage, AIMessage
import mapper
import services
from mapper.chat_history_mapper import save_messages


class AIServer(object):
    def __init__(self, user_id: str, lover_id: str):
        self.user_id = user_id
        self.lover_id = lover_id

    async def sse_chat(self, content: str):
        """SSE chat: validates user-lover pair, generates response, yields SSE events"""
        try:
            record = mapper.get_user_lover(user_id=self.user_id, lover_id=self.lover_id)
            logging.info(f"find lover info success {record}")
        except Exception as e:
            logging.error(f"[db] query error, userId={self.user_id}, lover_id={self.lover_id}, e={e}")
            yield f"data: {json.dumps({'type': 'error', 'content': 'Invalid user pair'})}\n\n"
            return

        session_id = f'{self.user_id}_{self.lover_id}'

        try:
            prompt = self.get_prompt_text()
            agent = services.PersonalityLoverAgent()
            full_response = await agent.run(query=content, session_id=session_id, persona_text=prompt)

            await save_messages(
                session_id=session_id,
                messages=[HumanMessage(content=content), AIMessage(content=full_response)]
            )

            yield f"data: {json.dumps({'type': 'message', 'content': full_response})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            logging.error(f"[sse] generate error={e}")
            yield f"data: {json.dumps({'type': 'error', 'content': 'Internal error'})}\n\n"

    def get_prompt_text(self):
        prompt_text = mapper.get_active_prompt(self.lover_id).prompt_text
        print(prompt_text)
        return prompt_text
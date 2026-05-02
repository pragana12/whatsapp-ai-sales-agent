from pydantic import BaseModel, ConfigDict


class EvolutionMessageKey(BaseModel):
    remoteJid: str
    fromMe: bool


class EvolutionExtendedTextMessage(BaseModel):
    text: str


class EvolutionInboundMessage(BaseModel):
    conversation: str | None = None
    extendedTextMessage: EvolutionExtendedTextMessage | None = None


class EvolutionMessageData(BaseModel):
    key: EvolutionMessageKey
    message: EvolutionInboundMessage


class EvolutionWebhookPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    event: str
    data: EvolutionMessageData

    def extract_text(self) -> str | None:
        message = self.data.message
        if message.extendedTextMessage is not None:
            return message.extendedTextMessage.text
        return message.conversation


class HealthResponse(BaseModel):
    status: str
    version: str
    chroma_ready: bool
    evolution_configured: bool


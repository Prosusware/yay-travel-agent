import os
import sys
import time
from typing import List, Dict, Any, Optional, Callable, Type, Annotated
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

# Add the WhatsApp MCP server to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'whatsapp-mcp', 'whatsapp-mcp-server'))

from whatsapp import (
    list_messages as whatsapp_list_messages,
    list_chats as whatsapp_list_chats,
    get_chat as whatsapp_get_chat,
    get_direct_chat_by_contact as whatsapp_get_direct_chat_by_contact,
    get_contact_chats as whatsapp_get_contact_chats,
    get_last_interaction as whatsapp_get_last_interaction,
    get_message_context as whatsapp_get_message_context,
    send_message as whatsapp_send_message,
    send_file as whatsapp_send_file,
    send_audio_message as whatsapp_audio_voice_message,
    download_media as whatsapp_download_media,
    send_read_receipt as whatsapp_send_read_receipt
)

# Tool input schemas
class ListMessagesInput(BaseModel):
    after: Optional[str] = Field(None, description="Optional ISO-8601 formatted string to only return messages after this date")
    before: Optional[str] = Field(None, description="Optional ISO-8601 formatted string to only return messages before this date")
    sender_phone_number: Optional[str] = Field(None, description="Optional phone number to filter messages by sender")
    chat_jid: Optional[str] = Field(None, description="Optional chat JID to filter messages by chat")
    query: Optional[str] = Field(None, description="Optional search term to filter messages by content")
    limit: int = Field(20, description="Maximum number of messages to return")
    page: int = Field(0, description="Page number for pagination")
    include_context: bool = Field(True, description="Whether to include messages before and after matches")
    context_before: int = Field(1, description="Number of messages to include before each match")
    context_after: int = Field(1, description="Number of messages to include after each match")

class ListChatsInput(BaseModel):
    query: Optional[str] = Field(None, description="Optional search term to filter chats by name or JID")
    limit: int = Field(20, description="Maximum number of chats to return")
    page: int = Field(0, description="Page number for pagination")
    include_last_message: bool = Field(True, description="Whether to include the last message in each chat")
    sort_by: str = Field("last_active", description="Field to sort results by, either 'last_active' or 'name'")

class GetChatInput(BaseModel):
    chat_jid: str = Field(description="The JID of the chat to retrieve")
    include_last_message: bool = Field(True, description="Whether to include the last message")

class GetDirectChatByContactInput(BaseModel):
    sender_phone_number: str = Field(description="The phone number to search for")

class GetContactChatsInput(BaseModel):
    jid: str = Field(description="The contact's JID to search for")
    limit: int = Field(20, description="Maximum number of chats to return")
    page: int = Field(0, description="Page number for pagination")

class GetLastInteractionInput(BaseModel):
    jid: str = Field(description="The JID of the contact to search for")

class GetMessageContextInput(BaseModel):
    message_id: str = Field(description="The ID of the message to get context for")
    before: int = Field(5, description="Number of messages to include before the target message")
    after: int = Field(5, description="Number of messages to include after the target message")

class SendMessageInput(BaseModel):
    recipient: str = Field(description="The recipient - either a phone number with country code but no + or other symbols, or a JID")
    message: str = Field(description="The message text to send")

class SendFileInput(BaseModel):
    recipient: str = Field(description="The recipient - either a phone number with country code but no + or other symbols, or a JID")
    media_path: str = Field(description="The absolute path to the media file to send")

class SendAudioMessageInput(BaseModel):
    recipient: str = Field(description="The recipient - either a phone number with country code but no + or other symbols, or a JID")
    media_path: str = Field(description="The absolute path to the audio file to send")

class DownloadMediaInput(BaseModel):
    message_id: str = Field(description="The ID of the message containing the media")
    chat_jid: str = Field(description="The JID of the chat containing the message")

class SendReadReceiptInput(BaseModel):
    message_id: str = Field(description="The ID of the message to mark as read")
    chat_jid: str = Field(description="The JID of the chat containing the message")
    sender_jid: Optional[str] = Field(None, description="The JID of the sender (required for group chats, optional for direct chats)")

# Simple in-memory cache for recent messages to prevent duplicates
_recent_messages = {}  # Format: {recipient: [(message, timestamp)]}
_MESSAGE_EXPIRY_TIME = 60  # Messages expire after 60 seconds

class ListMessagesTool(BaseTool):
    name: str = "list_messages"
    description: str = "Get WhatsApp messages matching specified criteria with optional context"
    args_schema: Type[BaseModel] = ListMessagesInput

    def _run(self, **kwargs) -> List[Dict[str, Any]]:
        return whatsapp_list_messages(**kwargs)

class ListChatsTool(BaseTool):
    name: str = "list_chats"
    description: str = "Get WhatsApp chats matching specified criteria"
    args_schema: Type[BaseModel] = ListChatsInput

    def _run(self, **kwargs) -> List[Dict[str, Any]]:
        return whatsapp_list_chats(**kwargs)

class GetChatTool(BaseTool):
    name: str = "get_chat"
    description: str = "Get WhatsApp chat metadata by JID"
    args_schema: Type[BaseModel] = GetChatInput

    def _run(self, chat_jid: str, include_last_message: bool = True) -> Dict[str, Any]:
        return whatsapp_get_chat(chat_jid, include_last_message)

class GetDirectChatByContactTool(BaseTool):
    name: str = "get_direct_chat_by_contact"
    description: str = "Get WhatsApp chat metadata by sender phone number"
    args_schema: Type[BaseModel] = GetDirectChatByContactInput

    def _run(self, sender_phone_number: str) -> Dict[str, Any]:
        return whatsapp_get_direct_chat_by_contact(sender_phone_number)

class GetContactChatsTool(BaseTool):
    name: str = "get_contact_chats"
    description: str = "Get all WhatsApp chats involving the contact"
    args_schema: Type[BaseModel] = GetContactChatsInput

    def _run(self, jid: str, limit: int = 20, page: int = 0) -> List[Dict[str, Any]]:
        return whatsapp_get_contact_chats(jid, limit, page)

class GetLastInteractionTool(BaseTool):
    name: str = "get_last_interaction"
    description: str = "Get most recent WhatsApp message involving the contact"
    args_schema: Type[BaseModel] = GetLastInteractionInput

    def _run(self, jid: str) -> str:
        return whatsapp_get_last_interaction(jid)

class GetMessageContextTool(BaseTool):
    name: str = "get_message_context"
    description: str = "Get context around a specific WhatsApp message"
    args_schema: Type[BaseModel] = GetMessageContextInput

    def _run(self, message_id: str, before: int = 5, after: int = 5) -> Dict[str, Any]:
        return whatsapp_get_message_context(message_id, before, after)

class SendMessageTool(BaseTool):
    name: str = "send_message"
    description: str = "Send a WhatsApp message to a person or group"
    args_schema: Type[BaseModel] = SendMessageInput

    def _run(self, recipient: str, message: str) -> Dict[str, Any]:
        if not recipient:
            return {"success": False, "message": "Recipient must be provided"}
        
        # Check for duplicate messages
        current_time = time.time()
        
        # Clean up expired messages
        if recipient in _recent_messages:
            _recent_messages[recipient] = [(msg, ts) for msg, ts in _recent_messages[recipient] 
                                          if current_time - ts < _MESSAGE_EXPIRY_TIME]
        
        # Check if this is a duplicate message
        if recipient in _recent_messages:
            for recent_msg, _ in _recent_messages[recipient]:
                if recent_msg == message:
                    return {"success": False, "message": "Duplicate message detected. Prevented sending."}
        
        # Send the message
        success, status_message = whatsapp_send_message(recipient, message)
        
        # If successful, add to recent messages
        if success:
            if recipient not in _recent_messages:
                _recent_messages[recipient] = []
            _recent_messages[recipient].append((message, current_time))
        
        return {"success": success, "message": status_message}

class SendFileTool(BaseTool):
    name: str = "send_file"
    description: str = "Send a file such as a picture, raw audio, video or document via WhatsApp"
    args_schema: Type[BaseModel] = SendFileInput

    def _run(self, recipient: str, media_path: str) -> Dict[str, Any]:
        success, status_message = whatsapp_send_file(recipient, media_path)
        return {"success": success, "message": status_message}

class SendAudioMessageTool(BaseTool):
    name: str = "send_audio_message"
    description: str = "Send any audio file as a WhatsApp audio message"
    args_schema: Type[BaseModel] = SendAudioMessageInput

    def _run(self, recipient: str, media_path: str) -> Dict[str, Any]:
        success, status_message = whatsapp_audio_voice_message(recipient, media_path)
        return {"success": success, "message": status_message}

class DownloadMediaTool(BaseTool):
    name: str = "download_media"
    description: str = "Download media from a WhatsApp message and get the local file path"
    args_schema: Type[BaseModel] = DownloadMediaInput

    def _run(self, message_id: str, chat_jid: str) -> Dict[str, Any]:
        file_path = whatsapp_download_media(message_id, chat_jid)
        
        if file_path:
            return {
                "success": True,
                "message": "Media downloaded successfully",
                "file_path": file_path
            }
        else:
            return {
                "success": False,
                "message": "Failed to download media"
            }

class SendReadReceiptTool(BaseTool):
    name: str = "send_read_receipt"
    description: str = "Send a read receipt for a WhatsApp message to mark it as read"
    args_schema: Type[BaseModel] = SendReadReceiptInput

    def _run(self, message_id: str, chat_jid: str, sender_jid: Optional[str] = None) -> Dict[str, Any]:
        success, status_message = whatsapp_send_read_receipt(message_id, chat_jid, sender_jid)
        return {"success": success, "message": status_message}

# Export all tools
def get_whatsapp_tools():
    """Return all WhatsApp tools for the agent"""
    return [
        ListMessagesTool(),
        ListChatsTool(),
        GetChatTool(),
        GetDirectChatByContactTool(),
        GetContactChatsTool(),
        GetLastInteractionTool(),
        GetMessageContextTool(),
        SendMessageTool(),
        SendFileTool(),
        SendAudioMessageTool(),
        DownloadMediaTool(),
        SendReadReceiptTool()
    ] 
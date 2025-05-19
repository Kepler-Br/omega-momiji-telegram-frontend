from prometheus_client import Counter, Gauge

# Message counters
prometheus_frontend_messages_caption = Counter('frontend_messages_caption', 'Total count of caption messages received')
prometheus_frontend_messages = Counter('frontend_messages', 'Total count of messages received')
prometheus_frontend_messages_document = Counter('frontend_messages_document', 'Total count of document messages received')
prometheus_frontend_messages_forwards = Counter('frontend_messages_forwards', 'Total count of forwards messages received')
prometheus_frontend_messages_group_chat_created = Counter('frontend_messages_group_chat_created', 'Total count of group chat created messages received')
prometheus_frontend_messages_left_chat_members = Counter('frontend_messages_left_chat_members', 'Total count of new chat members messages received')
prometheus_frontend_messages_location = Counter('frontend_messages_location', 'Total count of location messages received')
prometheus_frontend_messages_media = Counter('frontend_messages_media', 'Total count of media messages received')
prometheus_frontend_messages_new_chat_members = Counter('frontend_messages_new_chat_members', 'Total count of new chat members messages received')
prometheus_frontend_messages_new_chat_photo = Counter('frontend_messages_new_chat_photo', 'Total count of new chat photo messages received')
prometheus_frontend_messages_new_chat_title = Counter('frontend_messages_new_chat_title', 'Total count of new chat title messages received')
prometheus_frontend_messages_photo = Counter('frontend_messages_photo', 'Total count of photo messages received')
prometheus_frontend_messages_pinned_message = Counter('frontend_messages_pinned_message', 'Total count of pinned message messages received')
prometheus_frontend_messages_poll = Counter('frontend_messages_poll', 'Total count of poll messages received')
prometheus_frontend_messages_reactions = Counter('frontend_messages_reactions', 'Total count of reactions messages received')
prometheus_frontend_messages_service = Counter('frontend_messages_service', 'Total count of service messages received')
prometheus_frontend_messages_sticker = Counter('frontend_messages_sticker', 'Total count of sticker messages received')
prometheus_frontend_messages_supergroup_chat_created = Counter('frontend_messages_supergroup_chat_created', 'Total count of supergroupd chat created messages received')
prometheus_frontend_messages_text = Counter('frontend_messages_text', 'Total count of text messages received')
prometheus_frontend_messages_video_chat_ended = Counter('frontend_messages_video_chat_ended', 'Total count of video chat ended messages received')
prometheus_frontend_messages_video_chat_started = Counter('frontend_messages_video_chat_started', 'Total count of video chat started messages received')
prometheus_frontend_messages_video = Counter('frontend_messages_video', 'Total count of video messages received')
prometheus_frontend_messages_video_note = Counter('frontend_messages_video_note', 'Total count of video note messages received')
prometheus_frontend_messages_voice = Counter('frontend_messages_voice', 'Total count of voice messages received')

# Chat type counts
prometheus_frontend_known_bot_chats = Gauge('frontend_known_bot_chats', 'Total number of known bot type chats')
prometheus_frontend_known_channel_chats = Gauge('frontend_known_channel_chats', 'Total number of known channel type chats')
prometheus_frontend_known_group_chats = Gauge('frontend_known_group_chats', 'Total number of known group type chats')
prometheus_frontend_known_private_chats = Gauge('frontend_known_private_chats', 'Total number of known private type chats')
prometheus_frontend_known_supergroup_chats = Gauge('frontend_known_supergroup_chats', 'Total number of known supergroup type chats')
prometheus_frontend_known_unknown_chats = Gauge('frontend_known_unknown_chats', 'Total number of known unknown type chats')

# Users
prometheus_frontend_known_users = Gauge('frontend_known_users', 'Total number of known users')

-- 创建用户虚拟恋人配置表
CREATE TABLE user_lovers (
    id SERIAL PRIMARY KEY,

    user_id TEXT NOT NULL,
    lover_id TEXT NOT NULL,

    avatar TEXT ,
    name varchar(255) NOT NULL,

    gender SMALLINT NOT NULL CHECK (gender IN (0, 1)),
    personality SMALLINT NOT NULL,

    hobbies INTEGER[] NOT NULL,

    talking_style SMALLINT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 可选：添加业务唯一索引（防止一个用户重复创建同一个恋人）
CREATE UNIQUE INDEX idx_user_lovers_unique ON user_lovers (user_id, lover_id);

-- 可选：为 hobbies 数组添加 GIN 索引（如果常按兴趣查询）
-- CREATE INDEX idx_user_lovers_hobbies ON user_lovers USING GIN (hobbies);

CREATE TABLE bot_prompts (
    id SERIAL PRIMARY KEY,

    -- 机器人标识（外键或业务ID）
    bot_id TEXT NOT NULL,                -- 或者用 UUID / INT 引用 bots 表

    -- Prompt 内容（核心字段）
    prompt_text TEXT NOT NULL,

    -- 版本控制（重要！）
    version INT NOT NULL DEFAULT 1,

    -- 是否为当前生效版本
    is_active BOOLEAN NOT NULL DEFAULT false,

    -- 元信息（可选但强烈建议）
    description TEXT,                           -- 例如："v2 - 加入礼貌语气"
    tags TEXT[],                                -- 例如：ARRAY['onboarding', 'zh-CN']

    -- 创建/更新时间
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- 唯一约束：每个 bot 只能有一个 active 版本（可通过部分索引实现）
    CONSTRAINT unique_active_per_bot
        UNIQUE (bot_id, is_active)
        DEFERRABLE INITIALLY DEFERRED
);

-- 部分索引：确保每个 bot 最多只有一个 active = true 的记录
CREATE UNIQUE INDEX idx_bot_prompts_active_true
    ON bot_prompts (bot_id)
    WHERE is_active = true;

CREATE TABLE message_store (
    id BIGSERIAL PRIMARY KEY,

    -- 会话标识（session_id），由你定义（如 user_id + chat_id）
    session_id VARCHAR(128) NOT NULL,

    -- 消息类型：'human', 'ai', 'system', 'tool' 等（LangChain 标准）
    type VARCHAR(20) NOT NULL CHECK (type IN ('human', 'ai', 'system', 'tool', 'function')),

    -- 消息内容（纯文本或 JSON，取决于你的需求）
    content TEXT NOT NULL,

    -- 可选：额外元数据（如 tool_call_id, name 等）
    additional_kwargs JSONB DEFAULT '{}',

    -- 消息创建时间（用于排序和清理）
    created_at TIMESTAMPTZ NOT NOT NULL DEFAULT NOW()
);

-- 关键索引：按 session_id 快速查询 + 按时间排序
CREATE INDEX idx_message_store_session_id ON message_store (session_id);
CREATE INDEX idx_message_store_created_at ON message_store (created_at);
-- 联合索引（推荐）：高效获取某会话的最新 N 条消息
CREATE INDEX idx_message_store_session_time ON message_store (session_id, created_at);
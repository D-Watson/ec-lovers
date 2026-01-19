-- 创建用户虚拟恋人配置表
CREATE TABLE user_lovers (
    id SERIAL PRIMARY KEY,

    user_id TEXT NOT NULL,
    lover_id TEXT NOT NULL,

    avatar TEXT ,
    name TEXT NOT NULL CHECK (LENGTH(name) > 0 AND LENGTH(name) <= 50),

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
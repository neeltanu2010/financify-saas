create extension if not exists "uuid-ossp";

create table if not exists users (
  id uuid primary key default uuid_generate_v4(),
  email text unique not null,
  plan text not null default 'free',
  subscription_status text not null default 'inactive',
  surecart_customer_id text,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

create table if not exists tool_usage (
  id uuid primary key default uuid_generate_v4(),
  email text not null,
  tool_name text not null,
  usage_month text not null,
  usage_count int not null default 0,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now(),
  unique(email, tool_name, usage_month)
);

create table if not exists usage_logs (
  id uuid primary key default uuid_generate_v4(),
  email text not null,
  tool_name text not null,
  usage_month text not null,
  created_at timestamp with time zone default now()
);

create table if not exists subscriptions (
  id uuid primary key default uuid_generate_v4(),
  email text not null,
  plan text not null default 'pro',
  amount int not null default 499,
  status text not null default 'active',
  surecart_customer_id text,
  surecart_order_id text,
  created_at timestamp with time zone default now()
);

-- Recommended indexes
create index if not exists idx_users_email on users(email);
create index if not exists idx_tool_usage_email_tool_month on tool_usage(email, tool_name, usage_month);
create index if not exists idx_usage_logs_email_tool_month on usage_logs(email, tool_name, usage_month);

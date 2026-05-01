use reqwest::{header, Client};
use serde::Serialize;
use std::sync::Arc;

use crate::config::Config;

pub struct LLMClient {
    http_client: Arc<Client>,
}

#[derive(Debug, Serialize)]
struct ChatMessage {
    role: String,
    content: String,
}

#[derive(Debug, Serialize)]
struct ChatRequest {
    model: String,
    messages: Vec<ChatMessage>,
    max_tokens: u32,
    temperature: f32,
    stream: bool,
}

impl LLMClient {
    pub fn new() -> Self {
        Self {
            http_client: Arc::new(Client::new()),
        }
    }

    pub async fn send_message(
        &self,
        message: String,
        config: Config,
    ) -> Result<String, Box<dyn std::error::Error>> {
        let url = format!("{}/chat/completions", config.api_base);

        let request_body = ChatRequest {
            model: config.model,
            messages: vec![ChatMessage {
                role: "user".to_string(),
                content: message,
            }],
            max_tokens: config.max_tokens,
            temperature: config.temperature,
            stream: false,
        };

        let response = self
            .http_client
            .post(&url)
            .header(header::AUTHORIZATION, format!("Bearer {}", config.api_key))
            .header(header::CONTENT_TYPE, "application/json")
            .json(&request_body)
            .send()
            .await?;

        if !response.status().is_success() {
            let status = response.status();
            let text = response.text().await.unwrap_or_default();
            return Err(format!("请求失败 ({}): {}", status, text).into());
        }

        let json: serde_json::Value = response.json().await?;

        let content = json
            .get("choices")
            .and_then(|c| c.get(0))
            .and_then(|c| c.get("message"))
            .and_then(|m| m.get("content"))
            .and_then(|c| c.as_str())
            .unwrap_or("(空回复)")
            .to_string();

        Ok(content)
    }
}

pub async fn test_connection(
    api_base: String,
    api_key: String,
    model: String,
) -> Result<String, Box<dyn std::error::Error>> {
    let client = Client::new();
    let url = format!("{}/chat/completions", api_base);

    let request_body = ChatRequest {
        model,
        messages: vec![ChatMessage {
            role: "user".to_string(),
            content: "Hi".to_string(),
        }],
        max_tokens: 5,
        temperature: 0.0,
        stream: false,
    };

    let response = client
        .post(&url)
        .header(header::AUTHORIZATION, format!("Bearer {}", api_key))
        .header(header::CONTENT_TYPE, "application/json")
        .json(&request_body)
        .send()
        .await?;

    if !response.status().is_success() {
        let status = response.status();
        let text = response.text().await.unwrap_or_default();
        return Err(format!("连接失败 ({}): {}", status, text).into());
    }

    let json: serde_json::Value = response.json().await?;

    let content = json
        .get("choices")
        .and_then(|c| c.get(0))
        .and_then(|c| c.get("message"))
        .and_then(|m| m.get("content"))
        .and_then(|c| c.as_str())
        .unwrap_or("(空回复)")
        .to_string();

    Ok(format!(
        "连接成功，模型回复: {}",
        &content[..content.len().min(50)]
    ))
}

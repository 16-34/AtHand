use std::sync::{Arc, Mutex};
use tauri::{
    CustomMenuItem, Manager, SystemTray, SystemTrayEvent, SystemTrayMenu, SystemTrayMenuItem,
    WindowEvent,
};

mod config;
mod hotkey;
mod llm;

use config::Config;
use hotkey::HotkeyManager;
use llm::LLMClient;

#[derive(Clone)]
struct AppState {
    config: Arc<Mutex<Config>>,
    llm_client: Arc<LLMClient>,
}

fn main() {
    let config = Arc::new(Mutex::new(Config::load()));
    let llm_client = Arc::new(LLMClient::new());

    let app_state = AppState {
        config: config.clone(),
        llm_client: llm_client.clone(),
    };

    let show = CustomMenuItem::new("show".to_string(), "显示");
    let settings = CustomMenuItem::new("settings".to_string(), "设置");
    let quit = CustomMenuItem::new("quit".to_string(), "退出");

    let tray_menu = SystemTrayMenu::new()
        .add_item(show)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(settings)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(quit);

    let system_tray = SystemTray::new().with_menu(tray_menu);

    tauri::Builder::default()
        .system_tray(system_tray)
        .on_system_tray_event(|app, event| match event {
            SystemTrayEvent::LeftClick { .. } => {
                toggle_window(app);
            }
            SystemTrayEvent::MenuItemClick { id, .. } => match id.as_str() {
                "show" => toggle_window(app),
                "settings" => show_settings(app),
                "quit" => std::process::exit(0),
                _ => {}
            },
            _ => {}
        })
        .on_window_event(|event| {
            if let WindowEvent::CloseRequested { api, .. } = event.event() {
                event.window().hide().unwrap();
                api.prevent_close();
            }
        })
        .manage(app_state.clone())
        .invoke_handler(tauri::generate_handler![
            send_message,
            get_config,
            save_config,
            test_connection
        ])
        .setup(move |app| {
            let window = app.get_window("main").unwrap();

            let window_clone = window.clone();
            let hotkey_manager = HotkeyManager::new(move || {
                let _ = window_clone.show();
                let _ = window_clone.set_focus();
            });

            hotkey_manager.start();

            if config.lock().unwrap().api_key.is_empty() {
                let _ = window.show();
                let _ = window.emit("show-settings", ());
            }

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

fn toggle_window(app: &tauri::AppHandle) {
    if let Some(window) = app.get_window("main") {
        if window.is_visible().unwrap_or(false) {
            let _ = window.hide();
        } else {
            let _ = window.show();
            let _ = window.set_focus();
        }
    }
}

fn show_settings(app: &tauri::AppHandle) {
    if let Some(window) = app.get_window("main") {
        let _ = window.show();
        let _ = window.set_focus();
        let _ = window.emit("show-settings", ());
    }
}

#[tauri::command]
async fn send_message(
    message: String,
    state: tauri::State<'_, AppState>,
) -> Result<String, String> {
    let config = state.config.lock().unwrap().clone();

    if config.api_key.is_empty() {
        return Err("请先在设置中配置 API Key".to_string());
    }

    state
        .llm_client
        .send_message(message, config)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
fn get_config(state: tauri::State<'_, AppState>) -> Result<Config, String> {
    Ok(state.config.lock().unwrap().clone())
}

#[tauri::command]
fn save_config(new_config: Config, state: tauri::State<'_, AppState>) -> Result<(), String> {
    new_config.save().map_err(|e| e.to_string())?;
    *state.config.lock().unwrap() = new_config;
    Ok(())
}

#[tauri::command]
async fn test_connection(
    api_base: String,
    api_key: String,
    model: String,
) -> Result<String, String> {
    llm::test_connection(api_base, api_key, model)
        .await
        .map_err(|e| e.to_string())
}

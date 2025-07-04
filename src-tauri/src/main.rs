#![cfg_attr(
  all(not(debug_assertions), target_os = "windows"),
  windows_subsystem = "windows"
)]

use tauri::api::process::{Command, CommandEvent};
use tauri::Manager;
use std::collections::HashMap;
use std::time::Duration;
use async_std::task;

fn main() {
  tauri::Builder::default()
    .setup(|app| {
      let splashscreen_window = app.get_window("splashscreen").unwrap();
      let main_window = app.get_window("main").unwrap();

      let mut env = HashMap::new();
      env.insert("PYTHONUNBUFFERED".to_string(), "1".to_string());

      let (mut rx, _) = Command::new_sidecar("trame")
        .expect("failed to create sidecar")
        .args(["--server", "--port", "0", "--timeout", "10"])
        .envs(env)
        .spawn()
        .expect("Failed to spawn server");

      tauri::async_runtime::spawn(async move {
        while let Some(event) = rx.recv().await {
          match event {
            CommandEvent::Stdout(line) => {
              println!("Stdout: {}", line);
              if line.contains("tauri-server-port=") {
                let tokens: Vec<&str> = line.split("=").collect();
                let port_token = tokens[1].to_string();
                let port = port_token.trim();
                // println!("window.location.replace(window.location.href + '?sessionURL=ws://localhost:{}/ws')", port);
                let _ = main_window.eval(&format!("window.location.replace(window.location.href + '?sessionURL=ws://localhost:{}/ws')", port));
              }
              if line.contains("tauri-client-ready") {
                task::sleep(Duration::from_secs(2)).await;
                splashscreen_window.close().unwrap();
                main_window.show().unwrap();
              }
            },
            CommandEvent::Stderr(line) => {
              // Handle stderr output
              println!("Stderr: {}", line);
            },
            CommandEvent::Error(error) => {
              println!("[Trame error] {}", error);
            },
            CommandEvent::Terminated(code) => {
              println!("[Trame exited] with code {:?}", code);
            },
            _ => {},
          }
        }
      });
      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running application");
}
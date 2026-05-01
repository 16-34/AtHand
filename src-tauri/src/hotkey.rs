use rdev::{listen, EventType, Key};
use std::sync::Arc;
use std::time::{Duration, Instant};

pub struct HotkeyManager {
    callback: Arc<dyn Fn() + Send + Sync>,
}

impl HotkeyManager {
    pub fn new<F>(callback: F) -> Self
    where
        F: Fn() + Send + Sync + 'static,
    {
        Self {
            callback: Arc::new(callback),
        }
    }

    pub fn start(&self) {
        let callback = self.callback.clone();
        let mut last_shift_time: Option<Instant> = None;
        let double_shift_interval = Duration::from_millis(300);

        std::thread::spawn(move || {
            if let Err(error) = listen(move |event| {
                if let EventType::KeyPress(key) = event.event_type {
                    if Self::is_shift(&key) {
                        let now = Instant::now();

                        if let Some(last_time) = last_shift_time {
                            if now.duration_since(last_time) < double_shift_interval {
                                callback();
                                last_shift_time = None;
                            } else {
                                last_shift_time = Some(now);
                            }
                        } else {
                            last_shift_time = Some(now);
                        }
                    }
                }
            }) {
                eprintln!("热键监听错误: {:?}", error);
            }
        });
    }

    fn is_shift(key: &Key) -> bool {
        matches!(key, Key::ShiftLeft | Key::ShiftRight)
    }
}

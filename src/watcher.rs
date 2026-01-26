use notify::{Config, Error, Event, RecommendedWatcher, RecursiveMode, Watcher};
use std::ffi::CString;
use std::path::Path;
use std::sync::mpsc::{channel, Receiver, Sender};
use std::thread;

/// Enable hot reloading by watching the specified paths.
/// When a change is detected, this function restarts the current process.
#[allow(clippy::type_complexity)]
pub fn enable_hot_reload(path_str: String) {
    // Spawn a thread to handle watching
    thread::spawn(move || {
        let (tx, rx): (Sender<Result<Event, Error>>, Receiver<Result<Event, Error>>) = channel();

        // Initialize watcher
        let mut watcher: RecommendedWatcher = Watcher::new(tx, Config::default()).unwrap();

        // Watch the directory
        if let Err(e) = watcher.watch(Path::new(&path_str), RecursiveMode::Recursive) {
            eprintln!("❌ Failed to watch directory {}: {}", path_str, e);
            return;
        }

        println!("🔃 Hot-Reload: Active");

        // Wait for events
        loop {
            match rx.recv() {
                Ok(Ok(Event {
                    kind: notify::EventKind::Modify(_),
                    paths,
                    ..
                })) => {
                    // Filter out non-python files if needed, but for now watch all
                    // Simple debounce: Wait a bit to avoid multiple restarts for one save
                    if let Some(path) = paths.first() {
                        println!("Using: {}", path.display());
                    }
                    println!("🔄 Restarting...");
                    restart_process();
                }
                Ok(Err(e)) => eprintln!("watch error: {:?}", e),
                Err(e) => eprintln!("watch channel error: {:?}", e),
                _ => {} // Ignore other events for now
            }
        }
    });
}

#[cfg(unix)]
fn restart_process() {
    use nix::unistd::execvp;

    // Get current arguments
    let args: Vec<String> = std::env::args().collect();

    // Prepare CStrings for execvp
    let program = CString::new(args[0].clone()).unwrap();
    let c_args: Vec<CString> = args
        .iter()
        .map(|arg| CString::new(arg.clone()).unwrap())
        .collect();

    // Execvp replaces the current process
    // We need to pass the program name as the first argument as well in the args list?
    // Yes, execvp takes (program, args). The first arg in args is conventionally the program name.

    // CAUTION: execvp expects the args slice to include the program name at index 0.
    // std::env::args() includes it at index 0.

    match execvp(&program, &c_args) {
        Ok(_) => {
            // Should never be reached
        }
        Err(e) => {
            eprintln!("❌ Failed to restart process: {}", e);
        }
    }
}

#[cfg(not(unix))]
fn restart_process() {
    eprintln!("⚠️ Process restarting is currently visible only on Unix-like systems.");
    eprintln!("⚠️ Please manually restart the server to apply changes.");
}

use minijinja::{path_loader, Environment};

pub type TemplateEnv = Environment<'static>;

pub fn create_env(template_folder: Option<String>) -> TemplateEnv {
    let mut env = Environment::new();
    let folder = template_folder.unwrap_or_else(|| "templates".to_string());

    // Use path_loader to load templates from filesystem
    env.set_loader(path_loader(folder));

    env
}

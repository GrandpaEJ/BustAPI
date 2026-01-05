fn main() {
    let body = "\n    <!DOCTYPE html>\n    <html>";
    let trimmed = body.trim();
    println!("Original: '{}'", body);
    println!("Trimmed: '{}'", trimmed);
    println!("Starts with <: {}", trimmed.starts_with("<"));
    
    if trimmed.starts_with("<") {
        println!("DETECTED: HTML");
    } else {
        println!("DETECTED: OTHER");
    }
}

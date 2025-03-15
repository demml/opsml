use owo_colors::{OwoColorize, Rgb};
pub struct Colorize {}

impl Colorize {
    #[must_use]
    pub fn purple(text: &str) -> String {
        // use #4B3978 as purple color
        let purple = Rgb(75, 57, 120);

        text.color(purple).to_string()
    }

    #[must_use]
    pub fn green(text: &str) -> String {
        // use #04cd9b as green color
        let green = Rgb(4, 205, 155);

        text.color(green).to_string()
    }

    #[must_use]
    pub fn alert(text: &str) -> String {
        // use #FF0000 as red color
        let red = Rgb(255, 0, 0);

        text.color(red).to_string()
    }
}

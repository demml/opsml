use opsml_colors::Colorize;

pub fn interface_error() -> String {
    let error = Colorize::alert("Error: Interface attribute must be an instance of ModelInterface");
    let msg = Colorize::green("interface=interface # This should be a ModelInterface instance");
    format!(
        r#"
        
Explanation:
#################################################################################
# This is a ModelInterface instance
# The ModelCard interface attribute must be an instance of ModelInterface

{error}
    
my_model = MyModel()
interface = ModelInterface(my_model)

card = ModelCard(
        {msg}
    )

Check to ensure you are wrapping your model in a subclass of ModelInterface
#################################################################################
"#
    )
}

use clap::Parser;
use opsml_colors::Colorize;
use rayon::prelude::*;
use std::env;
use std::fs::File;
use std::io::{self, BufRead};
use std::path::Path;
use tabled::settings::object::{Columns, Rows};
use tabled::settings::{Alignment, Color, Style, Width, format::Format};
use tabled::{Table, Tabled};
use walkdir::WalkDir;

#[derive(Parser)]
#[command(name = "todo_scanner")]
#[command(about = "Scans a directory for TODO comments", long_about = None)]
struct Cli {
    /// The path to the directory to scan
    #[arg(short, long)]
    path: Option<String>,
}

struct Todo {
    line: String,

    file: String,

    comment: String,
}

#[derive(Tabled)]
struct TableRecord {
    #[tabled(rename = "#")]
    idx: String,

    #[tabled(rename = "Line")]
    line: String,

    #[tabled(rename = "File")]
    file: String,

    #[tabled(rename = "Comment")]
    comment: String,
}

fn main() -> io::Result<()> {
    let cli = Cli::parse();

    let parent_path = cli
        .path
        .unwrap_or_else(|| env::current_dir().unwrap().display().to_string());

    let entries: Vec<_> = WalkDir::new(&parent_path)
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|e| e.file_type().is_file())
        .collect();

    let todos: Vec<Todo> = entries
        .par_iter()
        .map(|entry| {
            let mut file_todos = Vec::new();
            let file_path = entry.path().display().to_string();

            // get relative path to file_path relative to parent_path
            let file_path = Path::new(&file_path)
                .strip_prefix(&parent_path)
                .unwrap_or(Path::new(&file_path))
                .display()
                .to_string();

            let file = File::open(entry.path()).unwrap();

            let reader = io::BufReader::new(file);

            for (index, line) in reader.lines().enumerate() {
                if line.is_err() {
                    continue;
                }
                let line = line.unwrap();
                if let Some(pos) = line.find("TODO:") {
                    // Check if TODO is surrounded by quotation marks
                    let before = &line[..pos];
                    let after = &line[pos + 5..];
                    if !(before.trim_end().ends_with('"') && after.trim_start().starts_with('"')) {
                        let comment = after.trim().to_string();
                        let line_num = format!("{}", index + 1).to_string();
                        file_todos.push(Todo {
                            line: line_num,
                            file: file_path.clone() + ":" + &(index + 1).to_string(),
                            comment,
                        });
                    }
                }
            }
            file_todos
        })
        .flatten()
        .collect();

    if todos.is_empty() {
        println!("{}", Colorize::green("******** No TODOs to do! ********"));
        return Ok(());
    }

    // iterate and enumerate the todos and add them to TableRecord
    let todos: Vec<TableRecord> = todos
        .iter()
        .enumerate()
        .map(|(idx, todo)| TableRecord {
            idx: Colorize::purple(&format!("{}", idx + 1)),
            line: todo.line.clone(),
            file: todo.file.clone(),
            comment: todo.comment.clone(),
        })
        .collect();

    let mut table = Table::new(todos);

    table.with(Style::sharp());
    table.modify(Columns::one(0), Width::wrap(10).keep_words(true));
    table.modify(Columns::one(1), Width::wrap(10).keep_words(true));
    table.modify(Columns::one(2), Width::wrap(50));
    table.modify(Columns::one(3), Width::wrap(100).keep_words(true));
    table.modify(
        Rows::new(0..1),
        (
            Format::content(Colorize::green),
            Alignment::center(),
            Color::BOLD,
        ),
    );

    println!("{}", &table);
    Ok(())
}

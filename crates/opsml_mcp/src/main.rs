use anyhow::Result;
use opsml_mcp::handler::McpHandler;
use opsml_mcp::protocol::{JsonRpcRequest, JsonRpcResponse};
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader, BufWriter, Lines, Stdin};

#[tokio::main]
async fn main() -> Result<()> {
    // Tracing MUST go to stderr — stdout is the JSON-RPC stream.
    tracing_subscriber::fmt()
        .with_writer(std::io::stderr)
        .init();

    let handler = McpHandler;
    let mut reader: Lines<BufReader<Stdin>> = BufReader::new(tokio::io::stdin()).lines();
    let mut writer = BufWriter::new(tokio::io::stdout());

    while let Some(line) = reader.next_line().await? {
        if line.trim().is_empty() {
            continue;
        }

        let resp: JsonRpcResponse = match serde_json::from_str::<JsonRpcRequest>(&line) {
            Ok(req) => handler.handle(req),
            Err(e) => JsonRpcResponse::err(None, -32700, format!("Parse error: {e}")),
        };

        writer
            .write_all(serde_json::to_string(&resp)?.as_bytes())
            .await?;
        writer.write_all(b"\n").await?;
        writer.flush().await?;
    }

    Ok(())
}

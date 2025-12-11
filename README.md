# LogStream - Real-Time Log Aggregation System

LogStream is a lightweight, high-performance log aggregation system designed to ingest, process, and visualize logs in real-time. It acts as a simplified "Mini-ELK" stack, offering multi-protocol ingestion (TCP/UDP), streaming log parsing, in-memory indexing, and a premium web-based dashboard for monitoring and analysis.

## Features

*   **Multi-Protocol Ingestion**: Simultaneously accepts logs via TCP (default port 9001) and UDP (default port 9000).
*   **Real-Time Streaming**: Utilizes WebSockets to push new logs instantly to connected clients without polling.
*   **In-Memory Storage**: Efficient circular buffer storage for recent logs (configurable size) with search and filtering capabilities.
*   **Dynamic Parsing**: Automatically detects log levels (INFO, ERROR, WARN, DEBUG) and parses common metadata like service names.
*   **Interactive Dashboard**: A modern, dark-themed web interface for viewing live logs, filtering by service or level, and text searching.
*   **Zero Dependencies**: The core backend is built with standard Python asyncio libraries, requiring only FastAPI for the web layer.

## Project Structure

*   `main.py`: The entry point for the application. It initializes the FastAPI server, WebSocket endpoints, and background log ingestors.
*   `backend/`: Contains the core logic.
    *   `ingestor.py`: Handles the async TCP and UDP servers for receiving raw log data.
    *   `storage.py`: Manages in-memory log storage, indexing, and subscription handling for real-time updates.
*   `static/`: Frontend assets.
    *   `index.html`: The main dashboard structure.
    *   `style.css`: Premium dark-mode styling with glassmorphism effects.
    *   `app.js`: WebSocket client logic and dynamic UI rendering.
*   `test_logger.py`: A utility script to generate synthetic traffic for testing purposes.

## Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/abhi3114-glitch/LogStream.git
    cd LogStream
    ```

2.  **Set Up Virtual Environment** (Optional but recommended)
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Start the Server**
    Run the main application using Python:
    ```bash
    python main.py
    ```
    The server will start on `http://0.0.0.0:8000`.

2.  **Access the Dashboard**
    Open your web browser and navigate to `http://localhost:8000`. You will see the LogStream dashboard.

3.  **Ingest Logs**
    You can send logs to the system using any TCP or UDP client.
    
    **UDP Example (using Netcat):**
    ```bash
    echo "ERROR [payment-service] Transaction failed" | nc -u localhost 9000
    ```

    **TCP Example:**
    ```bash
    echo "INFO [auth] User logged in" | nc localhost 9001
    ```

4.  **Run Test Traffic**
    To simulate a busy production environment, run the included test script:
    ```bash
    python test_logger.py
    ```
    This will flood the system with random logs across various services and levels.

## Configuration

You can modify `main.py` to change the default ports:
*   UDP Port: 9000
*   TCP Port: 9001
*   Web Port: 8000
*   Buffer Size: 10,000 logs (in `LogStorage` class)

## License

This project is open-source and available under the MIT License.

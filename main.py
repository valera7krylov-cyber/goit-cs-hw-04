import threading
import multiprocessing
import time


def search_in_file(file_path, keywords):
    """Search for keywords in a single text file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read().lower()

            results = {}
            for keyword in keywords:
                if keyword.lower() in text:
                    results[keyword] = [file_path]
                else:
                    results[keyword] = []

    except OSError as error:
        print(f"Error reading {file_path}: {error}")
        return {}

    return results


def search_in_files(file_paths, keywords):
    """Search for keywords in a list of files."""
    results = {keyword: [] for keyword in keywords}

    for file_path in file_paths:
        file_result = search_in_file(file_path, keywords)

        for keyword in file_result:
            if file_result[keyword]:
                results[keyword].extend(file_result[keyword])

    return results


def search_in_files_thread(file_paths, keywords, results_list):
    """Search files in a thread and store the results."""
    results = search_in_files(file_paths, keywords)
    results_list.append(results)


def search_in_files_process(file_paths, keywords, result_queue):
    """Search files in a separate process and send results to a queue."""
    results = search_in_files(file_paths, keywords)
    result_queue.put(results)


if __name__ == "__main__":
    keywords = ["Python", "Java", "threading"]
    files = [
        "texts/file1.txt",
        "texts/file2.txt",
        "texts/file3.txt",
    ]
    num_threads = 2
    num_processes = 2
    result_queue = multiprocessing.Queue()
    chunk_size = (len(files) + num_threads - 1) // num_threads
    process_chunk_size = (len(files) + num_processes - 1) // num_processes

    process_start_time = time.perf_counter()
    processes = []

    for i in range(num_processes):
        start = i * process_chunk_size
        end = start + process_chunk_size
        file_chunk = files[start:end]

        process = multiprocessing.Process(
            target=search_in_files_process, args=(file_chunk, keywords, result_queue)
        )
        processes.append(process)
        process.start()

    process_results = []

    for _ in range(num_processes):
        process_result = result_queue.get()
        process_results.append(process_result)

    for process in processes:
        process.join()

    result_queue.close()
    result_queue.join_thread()

    process_results_combined = {keyword: [] for keyword in keywords}

    for process_result in process_results:
        for keyword in process_result:
            process_results_combined[keyword].extend(process_result[keyword])

    process_end_time = time.perf_counter()
    print(
        f"Multiprocessing execution time: "
        f"{process_end_time - process_start_time:.6f} seconds"
    )
    print(process_results_combined)

    threads = []
    thread_results = []

    start_time = time.perf_counter()
    for i in range(num_threads):
        start = i * chunk_size
        end = start + chunk_size
        file_chunk = files[start:end]

        thread = threading.Thread(
            target=search_in_files_thread, args=(file_chunk, keywords, thread_results)
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    results = {keyword: [] for keyword in keywords}
    for thread_result in thread_results:
        for keyword in thread_result:
            results[keyword].extend(thread_result[keyword])

    end_time = time.perf_counter()
    print(f"Threading execution time: {end_time - start_time:.6f} seconds")
    print(results)

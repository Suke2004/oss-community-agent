#include <iostream>
#include <cstdlib>
#include <string>

// Function to call the Python scraping script
void run_scraper(const std::string& url, const std::string& prompt) {
    std::string command = "python tools/scrape_tool.py \"" + url + "\" \"" + prompt + "\"";
    int result = std::system(command.c_str());
    if (result != 0) {
        std::cerr << "Error: The Python scraping script failed to run." << std::endl;
    }
}

int main() {
    // Example usage
    std::string target_url = "https://example.com";
    std::string extraction_prompt = "Extract all the product names and their prices.";
    run_scraper(target_url, extraction_prompt);
    return 0;
}
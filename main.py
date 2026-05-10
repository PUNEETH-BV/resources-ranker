import os
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

# Import scrapers
from scraper.youtube import get_youtube_resources
from scraper.reddit import get_reddit_resources
from scraper.medium import get_medium_resources
from scraper.sites import get_site_resources
from ranker.scorer import rank_resources

load_dotenv()
console = Console()

def main():
    console.print("[bold purple]Welcome to ResourceRank![/bold purple] 🚀", style="bold")
    
    # 1. User Input
    topic = Prompt.ask("[bold cyan]What topic do you want to study?[/bold cyan]")
    
    console.print("\n[bold yellow]--- Filters ---[/bold yellow]")
    console.print("[cyan]Content type options:[/cyan]")
    console.print("  [bold]1[/bold] - Video only (Searches YouTube)")
    console.print("  [bold]2[/bold] - Article only (Searches Medium, DEV.to, freeCodeCamp, etc.)")
    console.print("  [bold]3[/bold] - Both Videos & Articles")
    content_choice = Prompt.ask(
        "Select Content type", 
        choices=["1", "2", "3"], 
        default="3"
    )
    
    console.print("\n[cyan]Difficulty options:[/cyan]")
    console.print("  [bold]1[/bold] - Beginner")
    console.print("  [bold]2[/bold] - Intermediate")
    console.print("  [bold]3[/bold] - Advanced")
    console.print("  [bold]4[/bold] - All Difficulties")
    difficulty_choice = Prompt.ask(
        "Select Difficulty", 
        choices=["1", "2", "3", "4"], 
        default="4"
    )
    
    console.print("\n[cyan]Recency options:[/cyan]")
    console.print("  [bold]1[/bold] - Past Week")
    console.print("  [bold]2[/bold] - Past Month")
    console.print("  [bold]3[/bold] - Past Year")
    console.print("  [bold]4[/bold] - Any Time")
    recency_choice = Prompt.ask(
        "Select Recency", 
        choices=["1", "2", "3", "4"], 
        default="4"
    )
    
    free_only = Prompt.ask("\nFree only?", choices=["y", "n"], default="y")

    # Map choices
    difficulties = {"1": "Beginner", "2": "Intermediate", "3": "Advanced", "4": "All"}
    difficulty = difficulties[difficulty_choice]
    
    # 2. Parallel Scraping
    all_results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("[cyan]Scraping resources...", total=None)
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            
            # YouTube
            if content_choice in ["1", "3"]:
                futures.append(executor.submit(get_youtube_resources, topic, difficulty, recency_choice))
            
            # Reddit
            futures.append(executor.submit(get_reddit_resources, topic, recency_choice))
            
            # Medium
            if content_choice in ["2", "3"]:
                futures.append(executor.submit(get_medium_resources, topic))
                
            # Study Sites
            if content_choice in ["2", "3"]:
                futures.append(executor.submit(get_site_resources, topic))
            
            for future in futures:
                try:
                    result = future.result()
                    if result:
                        all_results.extend(result)
                except Exception as e:
                    console.print(f"[bold red]Scraper Error:[/bold red] {e}")

    if not all_results:
        console.print("[bold red]No resources found. Please try a different topic.[/bold red]")
        return

    # 3. Scoring
    ranked_results = rank_resources(all_results, topic)

    # 4. Generate HTML
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Use absolute path so this works regardless of CWD
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "output")
    env = Environment(loader=FileSystemLoader(output_dir))
    template = env.get_template("template.html")
    
    filters_display = {
        "type": "Videos & Articles" if content_choice == "3" else ("Videos" if content_choice == "1" else "Articles"),
        "difficulty": difficulty,
        "recency": "Any time" if recency_choice == "4" else ("Week" if recency_choice == "1" else ("Month" if recency_choice == "2" else "Year")),
        "free_only": "Yes" if free_only == "y" else "No"
    }
    
    output_filename = os.path.join(base_dir, "output", f"results_{topic.replace(' ', '_')}_{timestamp}.html")
    
    html_content = template.render(
        topic=topic,
        resources=ranked_results,
        filters=filters_display,
        current_date=current_date
    )
    
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 5. Summary Table
    table = Table(title=f"ResourceRank Summary for '{topic}'")
    table.add_column("Source", style="cyan")
    table.add_column("Count", style="magenta")
    table.add_column("Avg Score", style="green")

    sources = {}
    for r in ranked_results:
        s = r["source_name"]
        if s not in sources: sources[s] = []
        sources[s].append(r["score"])

    for s, scores in sources.items():
        avg = sum(scores) / len(scores)
        table.add_row(s, str(len(scores)), f"{avg:.1f}")

    console.print(table)
    
    # 6. Final Steps
    abs_path = os.path.abspath(output_filename)
    console.print(f"\n[bold green]✅ ResourceRank complete![/bold green] Found {len(ranked_results)} resources.")
    console.print(f"Report generated: [link=file://{abs_path}]{output_filename}[/link]")
    
    webbrowser.open(f"file://{abs_path}")

if __name__ == "__main__":
    main()

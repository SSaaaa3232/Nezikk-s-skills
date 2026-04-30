#!/usr/bin/env python3
"""
Web Search via Worker API

This script performs web searches by calling the Worker API, which integrates with Brave Search.
Returns AI-generated summaries along with search results.
"""

import argparse
import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def check_environment():
    """Check required environment variables."""
    worker_url = os.environ.get('AGENT_WORKER_BASE_URL')
    worker_secret = os.environ.get('AGENT_WORKER_SECRET')
    sandbox_id = os.environ.get('FLY_APP_NAME', 'unknown')

    missing = []
    if not worker_url:
        missing.append("  - AGENT_WORKER_BASE_URL: Base URL of the Worker API")
    if not worker_secret:
        missing.append("  - AGENT_WORKER_SECRET: Authentication secret for Worker API")

    if missing:
        print('Error: Required environment variables are not set:', file=sys.stderr)
        print('\n'.join(missing), file=sys.stderr)
        sys.exit(1)

    return {
        'worker_url': worker_url,
        'worker_secret': worker_secret,
        'sandbox_id': sandbox_id,
    }


def search_web(env_config, query, count=10, summary=True, entity_info=True):
    """
    Perform web search using Worker API.

    Args:
        env_config: Dictionary with Worker URL and auth secret
        query: Search query string
        count: Number of results to return (1-20, default: 10)
        summary: Include AI-generated summary (default: True)
        entity_info: Include entity information in summary (default: True)

    Returns:
        Dictionary containing search results and summary
    """
    url = f"{env_config['worker_url']}/api/tool/web-search"

    # Prepare request payload
    payload = {
        'query': query,
        'count': min(count, 20),  # Max 20 results
        'summary': summary,
        'entityInfo': entity_info,
    }

    # Prepare request headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {env_config['worker_secret']}",
        'X-Sandbox-Id': env_config['sandbox_id'],
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    try:
        # Make HTTP request
        request = Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )

        with urlopen(request, timeout=30) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            return response_data

    except HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"HTTP Error {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"URL Error: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def format_results(data):
    """Format search results for display."""
    output = []

    # Add summary if available
    if data.get('summary') and data['summary'].get('text'):
        output.append("## Key Findings\n")
        output.append(data['summary']['text'])
        output.append("\n")

        # Add entity info if available
        if data['summary'].get('entity_info'):
            entity = data['summary']['entity_info']
            if entity.get('title') or entity.get('description'):
                output.append("\n### Entity Information")
                if entity.get('title'):
                    output.append(f"**{entity['title']}**")
                if entity.get('description'):
                    output.append(entity['description'])
                output.append("\n")

    # Add search results
    if data.get('results'):
        output.append(f"## Search Results ({data.get('count', 0)} results)\n")
        for i, result in enumerate(data['results'], 1):
            output.append(f"### {i}. {result['title']}")
            output.append(f"**URL:** {result['url']}")
            output.append(f"{result['description']}")
            if result.get('age'):
                output.append(f"*({result['age']})*")
            output.append("")
    else:
        output.append("No search results found.")

    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(
        description='Search the web using Brave Search API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic search
  python web_search.py "Python asyncio tutorial"

  # Search with more results
  python web_search.py "React hooks" --count 20

  # Search without AI summary
  python web_search.py "TypeScript types" --no-summary

  # Output raw JSON
  python web_search.py "Cloudflare Workers" --json

Environment Variables:
  AGENT_WORKER_BASE_URL - Worker API base URL (required)
  AGENT_WORKER_SECRET   - Worker API authentication secret (required)
  FLY_APP_NAME          - Sandbox ID (optional, defaults to 'unknown')
        """
    )

    parser.add_argument('query', help='Search query string')
    parser.add_argument(
        '--count', '-c',
        type=int,
        default=10,
        help='Number of results to return (1-20, default: 10)'
    )
    parser.add_argument(
        '--no-summary',
        action='store_true',
        help='Disable AI-generated summary'
    )
    parser.add_argument(
        '--no-entity-info',
        action='store_true',
        help='Disable entity information in summary'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output raw JSON response'
    )

    args = parser.parse_args()

    # Check environment
    env_config = check_environment()

    # Perform search
    results = search_web(
        env_config,
        args.query,
        count=args.count,
        summary=not args.no_summary,
        entity_info=not args.no_entity_info
    )

    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_results(results))


if __name__ == '__main__':
    main()

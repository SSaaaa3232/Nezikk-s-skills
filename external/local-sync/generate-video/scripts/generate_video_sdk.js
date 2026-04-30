#!/usr/bin/env node
/**
 * Generate videos using Trickle AI Gateway Client SDK
 */

const { createTrickleAIGatewayClient } = require('../lib/trickle-ai-gateway-client.js');
const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');

// Parse command line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    prompt: null,
    model: 'google/veo-3.1-generate-preview',
    duration: 6,
    aspectRatio: '16:9',
    output: 'generated_video.mp4',
    timeout: 300000, // 5 minutes in milliseconds
    initialDelay: 35000, // 35 seconds
    pollInterval: 5000 // 5 seconds
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--model':
        options.model = args[++i];
        break;
      case '--duration':
        options.duration = parseInt(args[++i]);
        break;
      case '--aspect-ratio':
        options.aspectRatio = args[++i];
        break;
      case '--output':
        options.output = args[++i];
        break;
      case '--timeout':
        options.timeout = parseInt(args[++i]) * 1000;
        break;
      case '--help':
      case '-h':
        showHelp();
        process.exit(0);
        break;
      default:
        if (!options.prompt) {
          options.prompt = args[i];
        }
        break;
    }
  }

  if (!options.prompt) {
    console.error('Error: Prompt is required\n');
    showHelp();
    process.exit(1);
  }

  return options;
}

function showHelp() {
  console.log(`
Usage: node generate_video_sdk.js "prompt" [options]

Generate videos from text prompts using AI Gateway SDK

Options:
  --model MODEL           Video model to use (default: google/veo-3.1-generate-preview)
  --duration SECONDS      Video duration in seconds (default: 6)
  --aspect-ratio RATIO    Video aspect ratio (default: 16:9)
  --output PATH           Output file path (default: generated_video.mp4)
  --timeout SECONDS       Maximum wait time in seconds (default: 300)
  -h, --help              Show this help message

Supported Models:
  - openai/sora-2
  - openai/sora-2-pro
  - google/veo-3.1-generate-preview (recommended)
  - google/veo-3.1-fast-generate-preview
  - byteplus/seedance-1-0-pro
  - byteplus/seedance-1-0-lite

Examples:
  node generate_video_sdk.js "A serene lake at sunset"
  node generate_video_sdk.js "City lights at night" --model openai/sora-2 --duration 8
  node generate_video_sdk.js "Dancing" --model byteplus/seedance-1-0-pro --aspect-ratio 9:16
`);
}

// Check API key
function checkApiKey() {
  const apiKey = process.env.AI_GATEWAY_API_KEY;
  if (!apiKey) {
    console.error('Error: AI_GATEWAY_API_KEY environment variable is required.');
    console.error('Please set it with your AI Gateway API key:');
    console.error('  export AI_GATEWAY_API_KEY="your-api-key-here"');
    process.exit(1);
  }
  return apiKey;
}

// Download file
function downloadFile(url, outputPath) {
  return new Promise((resolve, reject) => {
    const protocol = url.startsWith('https') ? https : http;
    const file = fs.createWriteStream(outputPath);

    protocol.get(url, (response) => {
      const totalSize = parseInt(response.headers['content-length'] || '0');
      let downloaded = 0;

      response.on('data', (chunk) => {
        downloaded += chunk.length;
        file.write(chunk);

        if (totalSize > 0) {
          const percent = ((downloaded / totalSize) * 100).toFixed(1);
          process.stdout.write(`\rDownloading: ${percent}%`);
        }
      });

      response.on('end', () => {
        file.end();
        console.log(''); // New line
        resolve();
      });

      response.on('error', reject);
    }).on('error', reject);
  });
}

// Main function
async function main() {
  const options = parseArgs();
  const apiKey = checkApiKey();

  try {
    // Create client
    const client = createTrickleAIGatewayClient({
      apiKey: apiKey,
      baseUrl: 'https://ai-gateway.trickle-lab.tech'
    });

    console.log('Generating video with SDK...');
    console.log(`Model: ${options.model}`);
    console.log(`Prompt: ${options.prompt}`);
    console.log(`Duration: ${options.duration}s, Aspect Ratio: ${options.aspectRatio}`);
    console.log('Submitting generation request...\n');

    const startTime = Date.now();

    // Generate video with automatic polling
    const videoStatus = await client.generateVideo(
      {
        model: options.model,
        prompt: options.prompt,
        duration: options.duration,
        aspectRatio: options.aspectRatio
      },
      {
        initialDelay: options.initialDelay,
        pollInterval: options.pollInterval,
        timeout: options.timeout,
        onStatusUpdate: (status) => {
          const elapsed = Math.floor((Date.now() - startTime) / 1000);
          process.stdout.write(`\rStatus: ${status.status} (elapsed: ${elapsed}s)`);
        }
      }
    );

    if (videoStatus.status === 'succeeded' && videoStatus.url) {
      console.log('\n✓ Video generation completed!');

      const outputPath = path.resolve(options.output);
      console.log(`Video URL: ${videoStatus.url}`);
      console.log(`Downloading to: ${outputPath}`);

      await downloadFile(videoStatus.url, outputPath);
      console.log(`✓ Video saved successfully to ${outputPath}`);
    } else if (videoStatus.status === 'failed') {
      console.log('\n✗ Video generation failed');
      console.error(`Error: ${videoStatus.error || 'Unknown error'}`);
      process.exit(1);
    } else {
      console.log(`\n⚠ Unexpected status: ${videoStatus.status}`);
      console.log('Video may still be processing.');
      process.exit(1);
    }

  } catch (error) {
    console.error('\n✗ Error:', error.message);
    if (error.statusCode) {
      console.error(`HTTP Status: ${error.statusCode}`);
    }
    if (error.response) {
      console.error(`Response: ${error.response}`);
    }
    process.exit(1);
  }
}

// Run main function
if (require.main === module) {
  main();
}

module.exports = { main };

/**
 * Text content in a message
 */
interface MessageContentText {
    type: 'text';
    text: string;
}
/**
 * Image URL content in a message for multi-modal requests
 */
interface MessageContentImageUrl {
    type: 'image_url';
    image_url: {
        url: string;
    };
}
/**
 * Message content can be either text or image URL (for multi-modal support)
 */
type MessageContent = MessageContentText | MessageContentImageUrl;
/**
 * Function tool parameter definition
 */
interface FunctionToolParameter {
    type: string | string[];
    description?: string;
    enum?: string[];
    items?: FunctionToolParameter;
    properties?: Record<string, FunctionToolParameter>;
    required?: string[];
    [key: string]: any;
}
/**
 * Tool definition for function calling
 */
interface Tool {
    type: 'function';
    function: {
        name: string;
        description?: string;
        parameters?: {
            type: "object";
            properties?: Record<string, FunctionToolParameter>;
            required?: string[];
            additionalProperties?: boolean;
        };
        strict?: boolean;
    };
}
/**
 * Tool choice strategy
 */
type ToolChoice = 'none' | 'auto' | 'required' | {
    type: 'function';
    function: {
        name: string;
    };
};
/**
 * Function call details
 */
interface FunctionCall {
    name: string;
    arguments: string;
    partial?: boolean;
}
/**
 * Tool call in assistant response
 */
interface ToolCall {
    id: string;
    type: 'function';
    function: FunctionCall;
    index?: number;
}
/**
 * A message in the conversation
 * - For text-only: use `content: string`
 * - For multi-modal: use `content: MessageContent[]` with mixed text and images
 */
interface Message {
    role: 'system' | 'user' | 'assistant';
    content: string | MessageContent[];
}
/**
 * Options for text generation
 *
 * @example
 * // Simple text generation
 * {
 *   model: "google/gemini-3-pro-preview",
 *   messages: [{ role: "user", content: "Hello!" }]
 * }
 *
 * @example
 * // With reasoning (for models that support it)
 * {
 *   model: "openai/gpt-5.1",
 *   messages: [{ role: "user", content: "Solve this problem..." }],
 *   reasoning: { max_tokens: 2000 }
 * }
 *
 * @example
 * // Multi-modal with image
 * {
 *   model: "google/gemini-3-pro-image-preview",
 *   messages: [{
 *     role: "user",
 *     content: [
 *       { type: "text", text: "What's in this image?" },
 *       { type: "image_url", image_url: { url: "https://..." } }
 *     ]
 *   }]
 * }
 */
interface GenerateTextOptions {
    /** Model identifier (e.g., "google/gemini-3-pro-preview", "anthropic/claude-sonnet-4.5") */
    model: string;
    /** Array of conversation messages */
    messages: Message[];
    /** Controls randomness (0.0 to 1.0). Lower is more deterministic. Default: 0.7 */
    temperature?: number;
    /** Maximum tokens to generate */
    max_tokens?: number;
    /** Nucleus sampling threshold (0.0 to 1.0) */
    top_p?: number;
    /** Stop sequences to end generation */
    stop?: string | string[];
    /** Enable streaming mode. If true, must provide callbacks as second parameter */
    stream?: boolean;
    /** Reasoning configuration for models that support chain-of-thought */
    reasoning?: {
        max_tokens?: number;
    };
    /** Tools/functions available for the model to call */
    tools?: Tool[];
    /** Strategy for tool selection */
    tool_choice?: ToolChoice;
    /** User identifier for tracking and analytics */
    user?: string;
}
/**
 * Response from text generation (non-streaming mode)
 */
interface GenerateTextResponse {
    id: string;
    object: string;
    created: number;
    model: string;
    choices: Array<{
        index: number;
        message: {
            role: string;
            /** Main generated text content */
            content: string;
            /** Reasoning/chain-of-thought content (if reasoning was enabled) */
            reasoning?: string;
            /** Tool calls made by the assistant */
            tool_calls?: ToolCall[];
        };
        finish_reason: string;
    }>;
    usage?: {
        prompt_tokens: number;
        completion_tokens: number;
        total_tokens: number;
        completion_tokens_details?: {
            reasoning_tokens?: number;
            accepted_prediction_tokens?: number;
            rejected_prediction_tokens?: number;
        };
    };
}
/**
 * A chunk of streamed text response
 */
interface StreamChunk {
    id: string;
    object: string;
    created: number;
    model: string;
    choices: Array<{
        index: number;
        delta: {
            role?: string;
            /** Incremental content in this chunk */
            content?: string;
            /** Incremental reasoning content in this chunk */
            reasoning?: string;
            /** Tool calls in this chunk */
            tool_calls?: ToolCall[];
        };
        /** null during streaming, set when complete */
        finish_reason: string | null;
    }>;
}
/**
 * Callbacks for streaming text generation
 *
 * @example
 * {
 *   onChunk: (chunk) => {
 *     const content = chunk.choices[0]?.delta?.content;
 *     if (content) console.log(content);
 *   },
 *   onComplete: () => console.log("Done!"),
 *   onError: (error) => console.error(error)
 * }
 */
interface StreamCallbacks {
    /** Called for each chunk of generated text */
    onChunk?: (chunk: StreamChunk) => void;
    /** Called when streaming is complete */
    onComplete?: () => void;
    /** Called if an error occurs during streaming */
    onError?: (error: Error) => void;
}
/**
 * Options for image generation
 *
 * @example
 * // Text-to-image generation
 * {
 *   model: "google/gemini-3-pro-image-preview",
 *   prompt: "A cute robot in a library",
 *   response_format: "url"
 * }
 *
 * @example
 * // Image-to-image transformation
 * {
 *   model: "openai/gpt-image-1",
 *   prompt: "Remove the background",
 *   images: ["https://example.com/input.jpg"],
 *   background: "transparent"
 * }
 */
interface GenerateImageOptions {
    /** Image model identifier (e.g., "google/gemini-3-pro-image-preview", "byteplus/seedream-4-5", "openai/gpt-image-1") */
    model: string;
    /** Text description of desired image or transformation */
    prompt: string;
    /** Reference images for image-to-image transformation (optional) */
    images?: string[];
    /** Number of images to generate. Default: 1 */
    n?: number;
    /** Image size specification (e.g., "1024x1024", "1536x1024") */
    size?: string;
    /** Aspect ratio (e.g., "1:1", "16:9", "3:4"). Alternative to size. */
    aspectRatio?: string;
    /** Output format: "url" returns image URL, "b64_json" returns base64 encoded image data. Default: "url" */
    response_format?: 'url' | 'b64_json';
    /** Background setting for compatible models (e.g., OpenAI gpt-image-1) */
    background?: 'transparent' | 'opaque' | 'auto';
    /** User identifier for tracking and analytics */
    user?: string;
}
/**
 * Response from image generation
 */
interface GenerateImageResponse {
    data: Array<{
        /** Image URL (if response_format is "url") */
        url?: string;
        /** Base64 encoded image data (if response_format is "b64_json") */
        b64_json?: string;
    }>;
    usage?: {
        prompt_tokens: number;
        completion_tokens: number;
        total_tokens: number;
    };
}
/**
 * Options for video generation
 *
 * @example
 * // Text-to-video generation
 * {
 *   model: "byteplus/seedance-1-0-pro",
 *   prompt: "A cinematic shot of waves crashing on a beach",
 *   duration: 5,
 *   aspectRatio: "16:9"
 * }
 *
 * @example
 * // Frame-guided video generation
 * {
 *   model: "byteplus/seedance-1-0-lite-i2v",
 *   prompt: "Camera pans across the landscape",
 *   first_frame: "https://example.com/start.jpg",
 *   last_frame: "data:image/png;base64,iVBORw0KGgoAAAANS...",
 *   duration: 8
 * }
 */
interface GenerateVideoOptions {
    /** Video model identifier (e.g., "byteplus/seedance-1-0-pro") */
    model: string;
    /** Text description of the desired video */
    prompt: string;
    /** Video duration in seconds (2-12 seconds). Default: 5 */
    duration?: number;
    /** Video aspect ratio (e.g., "16:9", "4:3", "1:1", "9:16"). Default: "16:9" */
    aspectRatio?: string;
    /** Resolution hint: "720p" or "1080p". Default: "720p" */
    size?: string;
    /** URL or base64 encoded image for starting frame (optional) */
    first_frame?: string;
    /** URL or base64 encoded image for ending frame (optional) */
    last_frame?: string;
    /** User identifier for tracking and analytics */
    user?: string;
}
/**
 * Response from video generation request
 * Contains the video ID for polling status
 */
interface GenerateVideoResponse {
    /** Unique identifier for the video generation task */
    id: string;
}
/**
 * Video status response with detailed information
 */
interface VideoStatus {
    /** Video ID */
    id: string;
    /** Upstream provider task ID */
    upstream_id: string | null;
    /** Model used for generation */
    model: string;
    /** Prompt used for generation */
    prompt: string;
    /** First frame URL if provided */
    first_frame: string | null;
    /** Last frame URL if provided */
    last_frame: string | null;
    /** Resolution specification */
    size: string | null;
    /** Aspect ratio */
    aspect_ratio: string | null;
    /** Video duration in seconds */
    duration: number | null;
    /** ISO 8601 timestamp of creation */
    created_at: string;
    /** ISO 8601 timestamp of completion */
    completed_at: string | null;
    /** Current status: "pending", "running", "succeeded", or "failed" */
    status: 'pending' | 'running' | 'succeeded' | 'failed';
    /** Error message if status is "failed" */
    error: string | null;
    /** Video URL if status is "succeeded" */
    url: string | null;
}
/**
 * List of videos with pagination info
 */
interface VideoListResponse {
    data: VideoStatus[];
    total: number;
    limit: number;
    offset: number;
}
/**
 * Options for polling video status
 */
interface PollVideoOptions {
    /** Time to wait before first status check in milliseconds. Default: 35000 (35 seconds) */
    initialDelay?: number;
    /** Interval between status checks in milliseconds. Default: 5000 (5 seconds) */
    pollInterval?: number;
    /** Maximum time to wait before timing out in milliseconds. Default: 300000 (5 minutes) */
    timeout?: number;
    /** Called on each status check */
    onStatusUpdate?: (status: VideoStatus) => void;
}
/**
 * Configuration for creating a Trickle AI Gateway client
 */
interface TrickleAIGatewayClientConfig {
    /** Your API key for authentication */
    apiKey: string;
    /** Base URL of the gateway. Default: "https://ai-gateway.samdy-chen-bca.workers.dev" */
    baseUrl?: string;
}
/**
 * Error thrown by the Trickle AI Gateway client
 */
declare class TrickleAIGatewayError extends Error {
    statusCode?: number | undefined;
    response?: any | undefined;
    constructor(message: string, statusCode?: number | undefined, response?: any | undefined);
}

declare class TrickleAIGatewayClient {
    private apiKey;
    private baseUrl;
    constructor(config: TrickleAIGatewayClientConfig);
    generateText(options: GenerateTextOptions & {
        stream?: false;
    }): Promise<GenerateTextResponse>;
    generateText(options: GenerateTextOptions & {
        stream: true;
    }, callbacks: StreamCallbacks): Promise<void>;
    private handleStreamResponse;
    generateImage(options: GenerateImageOptions): Promise<GenerateImageResponse>;
    generateVideo(options: GenerateVideoOptions, pollOptions?: PollVideoOptions): Promise<VideoStatus>;
    getVideoStatus(videoId: string): Promise<VideoStatus>;
    listVideos(limit?: number, offset?: number): Promise<VideoListResponse>;
    private pollVideoStatus;
    private sleep;
}
declare function createTrickleAIGatewayClient(config: TrickleAIGatewayClientConfig): TrickleAIGatewayClient;

export { TrickleAIGatewayClient, TrickleAIGatewayError, createTrickleAIGatewayClient };
export type { FunctionCall, FunctionToolParameter, GenerateImageOptions, GenerateImageResponse, GenerateTextOptions, GenerateTextResponse, GenerateVideoOptions, GenerateVideoResponse, Message, MessageContent, MessageContentImageUrl, MessageContentText, PollVideoOptions, StreamCallbacks, StreamChunk, Tool, ToolCall, ToolChoice, TrickleAIGatewayClientConfig, VideoListResponse, VideoStatus };

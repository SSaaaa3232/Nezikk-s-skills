'use strict';

/**
 * Error thrown by the Trickle AI Gateway client
 */
class TrickleAIGatewayError extends Error {
    constructor(message, statusCode, response) {
        super(message);
        this.statusCode = statusCode;
        this.response = response;
        this.name = 'TrickleAIGatewayError';
    }
}

class TrickleAIGatewayClient {
    constructor(config) {
        this.apiKey = config.apiKey;
        this.baseUrl = config.baseUrl || 'https://ai-gateway.trickle-lab.tech';
    }
    async generateText(options, callbacks) {
        const url = `${this.baseUrl}/api/v1/chat/completions`;
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.apiKey}`,
            'Origin': 'https://trickle.so'
        };
        const isStream = options.stream === true;
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers,
                body: JSON.stringify(options),
            });
            if (!response.ok) {
                const errorText = await response.text();
                throw new TrickleAIGatewayError(`API request failed: ${response.statusText}`, response.status, errorText);
            }
            if (isStream) {
                await this.handleStreamResponse(response, callbacks);
                return;
            }
            else {
                const data = await response.json();
                return data;
            }
        }
        catch (error) {
            if (error instanceof TrickleAIGatewayError) {
                throw error;
            }
            throw new TrickleAIGatewayError(error instanceof Error ? error.message : 'Unknown error occurred');
        }
    }
    async handleStreamResponse(response, callbacks) {
        const reader = response.body?.getReader();
        if (!reader) {
            throw new TrickleAIGatewayError('Response body is not readable');
        }
        const decoder = new TextDecoder();
        let buffer = '';
        try {
            while (true) {
                const { done, value } = await reader.read();
                if (done) {
                    callbacks.onComplete?.();
                    break;
                }
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';
                for (const line of lines) {
                    if (line.trim() === '')
                        continue;
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        if (data === '[DONE]') {
                            callbacks.onComplete?.();
                            return;
                        }
                        try {
                            const chunk = JSON.parse(data);
                            callbacks.onChunk?.(chunk);
                        }
                        catch (e) {
                            console.warn('Failed to parse SSE chunk:', e);
                        }
                    }
                }
            }
        }
        catch (error) {
            const err = error instanceof Error ? error : new Error('Stream processing failed');
            callbacks.onError?.(err);
            throw new TrickleAIGatewayError(err.message);
        }
    }
    async generateImage(options) {
        const url = `${this.baseUrl}/api/v1/images/generations`;
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.apiKey}`,
            'Origin': 'https://trickle.so'
        };
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers,
                body: JSON.stringify(options),
            });
            if (!response.ok) {
                const errorText = await response.text();
                throw new TrickleAIGatewayError(`API request failed: ${response.statusText}`, response.status, errorText);
            }
            const data = await response.json();
            return data;
        }
        catch (error) {
            if (error instanceof TrickleAIGatewayError) {
                throw error;
            }
            throw new TrickleAIGatewayError(error instanceof Error ? error.message : 'Unknown error occurred');
        }
    }
    async generateVideo(options, pollOptions) {
        const url = `${this.baseUrl}/api/v1/videos`;
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.apiKey}`,
            'Origin': 'https://trickle.so'
        };
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers,
                body: JSON.stringify(options),
            });
            if (!response.ok) {
                const errorText = await response.text();
                throw new TrickleAIGatewayError(`API request failed: ${response.statusText}`, response.status, errorText);
            }
            const data = await response.json();
            return await this.pollVideoStatus(data.id, pollOptions);
        }
        catch (error) {
            if (error instanceof TrickleAIGatewayError) {
                throw error;
            }
            throw new TrickleAIGatewayError(error instanceof Error ? error.message : 'Unknown error occurred');
        }
    }
    async getVideoStatus(videoId) {
        const url = `${this.baseUrl}/api/v1/videos/${videoId}`;
        const headers = {
            'Authorization': `Bearer ${this.apiKey}`,
            'Origin': 'https://trickle.so'
        };
        try {
            const response = await fetch(url, {
                method: 'GET',
                headers,
            });
            if (!response.ok) {
                const errorText = await response.text();
                throw new TrickleAIGatewayError(`API request failed: ${response.statusText}`, response.status, errorText);
            }
            const data = await response.json();
            return data;
        }
        catch (error) {
            if (error instanceof TrickleAIGatewayError) {
                throw error;
            }
            throw new TrickleAIGatewayError(error instanceof Error ? error.message : 'Unknown error occurred');
        }
    }
    async listVideos(limit = 10, offset = 0) {
        const url = `${this.baseUrl}/api/v1/videos?limit=${limit}&offset=${offset}`;
        const headers = {
            'Authorization': `Bearer ${this.apiKey}`,
            'Origin': 'https://trickle.so'
        };
        try {
            const response = await fetch(url, {
                method: 'GET',
                headers,
            });
            if (!response.ok) {
                const errorText = await response.text();
                throw new TrickleAIGatewayError(`API request failed: ${response.statusText}`, response.status, errorText);
            }
            const data = await response.json();
            return data;
        }
        catch (error) {
            if (error instanceof TrickleAIGatewayError) {
                throw error;
            }
            throw new TrickleAIGatewayError(error instanceof Error ? error.message : 'Unknown error occurred');
        }
    }
    async pollVideoStatus(videoId, pollOptions) {
        const initialDelay = pollOptions?.initialDelay ?? 35000;
        const pollInterval = pollOptions?.pollInterval ?? 5000;
        const timeout = pollOptions?.timeout ?? 300000;
        const startTime = Date.now();
        await this.sleep(initialDelay);
        while (true) {
            const elapsed = Date.now() - startTime;
            if (elapsed > timeout) {
                throw new TrickleAIGatewayError(`Video generation timed out after ${timeout}ms`);
            }
            const status = await this.getVideoStatus(videoId);
            pollOptions?.onStatusUpdate?.(status);
            if (status.status === 'succeeded') {
                return status;
            }
            if (status.status === 'failed') {
                throw new TrickleAIGatewayError(`Video generation failed: ${status.error || 'Unknown error'}`);
            }
            await this.sleep(pollInterval);
        }
    }
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}
function createTrickleAIGatewayClient(config) {
    return new TrickleAIGatewayClient(config);
}

exports.TrickleAIGatewayClient = TrickleAIGatewayClient;
exports.createTrickleAIGatewayClient = createTrickleAIGatewayClient;
//# sourceMappingURL=index.js.map

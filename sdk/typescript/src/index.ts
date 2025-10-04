/**
 * LLMScope TypeScript SDK
 */

export interface TrackEventOptions {
  model: string;
  provider: string;
  promptTokens: number;
  completionTokens: number;
  latencyMs: number;
  metadata?: Record<string, any>;
}

export class LLMTracker {
  private apiKey: string;
  private baseUrl: string;

  constructor(apiKey: string, baseUrl: string = "http://localhost:8000") {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async trackEvent(options: TrackEventOptions): Promise<void> {
    const eventData = {
      timestamp: new Date().toISOString(),
      model: options.model,
      provider: options.provider,
      prompt_tokens: options.promptTokens,
      completion_tokens: options.completionTokens,
      total_tokens: options.promptTokens + options.completionTokens,
      latency_ms: options.latencyMs,
      metadata: options.metadata || {},
    };

    try {
      const response = await fetch(`${this.baseUrl}/events/ingest`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": this.apiKey,
        },
        body: JSON.stringify(eventData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (error) {
      // Don't fail the main application if tracking fails
      console.error("LLMScope tracking error:", error);
    }
  }
}

export default LLMTracker;

import fs from 'fs/promises';
import path from 'path';
import { createHash } from 'crypto';

interface ErrorLog {
  timestamp: string;
  service: string;
  context: string;
  error_type: string;
  error_message: string;
  severity: string;
  stack_trace?: string;
  additional_data?: any;
  environment: string;
  version: string;
  request?: {
    method?: string;
    url?: string;
    headers?: any;
    user_agent?: string;
  };
}

interface ErrorPattern {
  pattern_hash: string;
  error_type: string;
  service: string;
  context: string;
  message: string;
  first_seen: string;
  last_seen: string;
  occurrence_count: number;
  resolved: boolean;
  solution?: string;
  prevention_tips: string[];
  related_errors: string[];
  severity: string;
}

export class ErrorCapture {
  private logDir: string;
  private serviceName: string;

  constructor() {
    this.logDir = path.join(__dirname, '../../logs/errors');
    this.serviceName = 'collab-engine';
    this.ensureLogDirectory();
  }

  private async ensureLogDirectory(): Promise<void> {
    try {
      await fs.mkdir(this.logDir, { recursive: true });
    } catch (error) {
      console.error('Failed to create log directory:', error);
    }
  }

  async logError(
    error: Error,
    context: string,
    request?: any,
    additionalData?: any
  ): Promise<void> {
    const errorLog: ErrorLog = {
      timestamp: new Date().toISOString(),
      service: this.serviceName,
      context,
      error_type: error.constructor.name,
      error_message: error.message,
      severity: this.determineSeverity(error),
      stack_trace: error.stack,
      additional_data: additionalData || {},
      environment: process.env.NODE_ENV || 'development',
      version: process.env.npm_package_version || '1.0.0',
    };

    // Add request context if available
    if (request) {
      errorLog.request = {
        method: request.method,
        url: request.url,
        headers: request.headers,
        user_agent: request.headers?.['user-agent'],
      };
    }

    // Log to structured error file
    await this.writeErrorLog(errorLog);

    // Send to error monitoring system
    await this.sendToMonitor(errorLog);

    // Update error guide if this is a new pattern
    await this.updateErrorGuide(errorLog);

    // Log to console for immediate visibility
    console.error(`[ERROR_CAPTURE] ${context}:`, {
      type: errorLog.error_type,
      severity: errorLog.severity,
      message: error.message,
    });
  }

  private determineSeverity(error: Error): string {
    const errorMessage = error.message.toLowerCase();
    const errorType = error.constructor.name;

    // Critical errors
    if (
      errorType === 'TypeError' ||
      errorType === 'ReferenceError' ||
      errorMessage.includes('out of memory') ||
      errorMessage.includes('segmentation fault')
    ) {
      return 'critical';
    }

    // High severity errors
    if (
      errorType === 'Error' ||
      errorMessage.includes('connection') ||
      errorMessage.includes('timeout') ||
      errorMessage.includes('database') ||
      errorMessage.includes('auth')
    ) {
      return 'high';
    }

    // Medium severity errors
    if (
      errorType === 'ValidationError' ||
      errorMessage.includes('invalid') ||
      errorMessage.includes('not found') ||
      errorMessage.includes('permission')
    ) {
      return 'medium';
    }

    return 'low';
  }

  private async writeErrorLog(errorLog: ErrorLog): Promise<void> {
    try {
      const logFile = path.join(this.logDir, `${this.serviceName}-errors.jsonl`);
      const logLine = JSON.stringify(errorLog) + '\n';
      await fs.appendFile(logFile, logLine);
    } catch (error) {
      console.error('Failed to write error log:', error);
    }
  }

  private async sendToMonitor(errorLog: ErrorLog): Promise<void> {
    try {
      const response = await fetch('http://localhost:8090/errors', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(errorLog),
        signal: AbortSignal.timeout(5000),
      });

      if (!response.ok) {
        console.warn('Failed to send error to monitor:', response.statusText);
      }
    } catch (error) {
      console.warn('Failed to send error to monitor:', error);
    }
  }

  private async updateErrorGuide(errorLog: ErrorLog): Promise<void> {
    try {
      // Create error pattern hash for deduplication
      const patternData = `${errorLog.error_type}${errorLog.error_message}`;
      const patternHash = createHash('md5').update(patternData).digest('hex');

      const newErrorEntry: ErrorPattern = {
        pattern_hash: patternHash,
        error_type: errorLog.error_type,
        service: errorLog.service,
        context: errorLog.context,
        message: errorLog.error_message,
        first_seen: errorLog.timestamp,
        last_seen: errorLog.timestamp,
        occurrence_count: 1,
        resolved: false,
        solution: undefined,
        prevention_tips: [],
        related_errors: [],
        severity: errorLog.severity,
      };

      // Write to pending errors file for review and integration
      const pendingFile = path.join(this.logDir, 'pending-error-patterns.jsonl');
      const entryLine = JSON.stringify(newErrorEntry) + '\n';
      await fs.appendFile(pendingFile, entryLine);
    } catch (error) {
      console.error('Failed to update error guide:', error);
    }
  }
}

// Global error capture instance
export const errorCapture = new ErrorCapture();

// Express middleware for error capture
export function errorCaptureMiddleware(
  error: Error,
  req: any,
  res: any,
  next: any
): void {
  // Capture the error
  errorCapture.logError(
    error,
    `${req.method} ${req.path}`,
    req,
    {
      body: req.body,
      params: req.params,
      query: req.query,
    }
  );

  // Send error response
  const statusCode = (error as any).statusCode || 500;
  res.status(statusCode).json({
    error: 'An error occurred',
    message: process.env.NODE_ENV === 'production' ? 'Internal Server Error' : error.message,
    timestamp: new Date().toISOString(),
  });
}

// WebSocket error capture
export class WebSocketErrorCapture {
  static async captureWebSocketError(
    error: Error,
    context: string,
    socketInfo?: any
  ): Promise<void> {
    await errorCapture.logError(
      error,
      `websocket_${context}`,
      undefined,
      {
        socket_id: socketInfo?.id,
        room: socketInfo?.room,
        user_id: socketInfo?.userId,
        connection_count: socketInfo?.connectionCount,
      }
    );
  }

  static async captureCollaborationError(
    error: Error,
    operation: string,
    documentId: string,
    userId?: string
  ): Promise<void> {
    await errorCapture.logError(
      error,
      `collaboration_${operation}`,
      undefined,
      {
        document_id: documentId,
        user_id: userId,
        operation,
      }
    );
  }

  static async captureEventStoreError(
    error: Error,
    streamId: string,
    eventType: string
  ): Promise<void> {
    await errorCapture.logError(
      error,
      'event_store_operation',
      undefined,
      {
        stream_id: streamId,
        event_type: eventType,
        event_store_url: process.env.EVENT_STORE_URL || 'http://localhost:8080',
      }
    );
  }
}

// Global error handlers
process.on('uncaughtException', async (error: Error) => {
  await errorCapture.logError(error, 'uncaught_exception');
  console.error('Uncaught Exception:', error);
  process.exit(1);
});

process.on('unhandledRejection', async (reason: any) => {
  const error = reason instanceof Error ? reason : new Error(String(reason));
  await errorCapture.logError(error, 'unhandled_rejection');
  console.error('Unhandled Rejection:', reason);
});

export default ErrorCapture;

import pino from "pino";

const logLevel = process.env.LOG_LEVEL || "debug";
export const logger = pino({ level: logLevel });

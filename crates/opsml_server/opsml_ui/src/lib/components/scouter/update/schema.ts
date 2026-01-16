// Functions and types use in the UpdataConfigModal
import { z } from "zod";
import { type AlertDispatchConfig } from "$lib/components/scouter/types";
import { type PsiThreshold } from "$lib/components/scouter/psi/types";
import {
  isCustomConfig,
  isGenAIConfig,
  isPsiConfig,
  isSpcConfig,
  type DriftConfigType,
} from "$lib/components/scouter/utils";

function stringToBoolean(str: string): boolean {
  return str.toLowerCase() === "true";
}

export const customConfigSchema = z.object({
  schedule: z.string().default("0 0 0 * * *"),
  sample: z.coerce.boolean().default(true),
  sample_size: z.coerce.number().default(25),
});

export const GenAIConfigSchema = z.object({
  schedule: z.string().default("0 0 0 * * *"),
  sample_ratio: z.coerce
    .number()
    .min(0, { message: "Value cannot be less than 0.0" })
    .max(1, { message: "Value cannot be greater than 1.0" }),
});

export const psiConfigSchema = z.object({
  schedule: z.string().default("0 0 0 * * *"),
  psi_threshold_value: z.coerce.number(),
  psi_threshold_type: z.string(),
  features_to_monitor: z.array(z.string()).default([]),
});

export const spcConfigSchema = z.object({
  schedule: z.string().default("0 0 0 * * *"),
  sample: z.coerce.boolean().default(true),
  sample_size: z.coerce.number().default(25),
  rule: z.string().default("8 16 4 8 2 4 1 1"),
  features_to_monitor: z.array(z.string()).default([]),
});

export const consoleSchema = z.object({
  enabled: z.coerce.boolean().default(false),
});

export const slackSchema = z.object({
  channel: z.string(),
});

export const opsGenieSchema = z.object({
  team: z.string(),
  priority: z.union([
    z.literal("p1"),
    z.literal("p2"),
    z.literal("p3"),
    z.literal("p4"),
    z.literal("p5"),
  ]),
});

export type ConfigType = "custom" | "psi";
export type ConfigSchemaMap = {
  custom: z.infer<typeof customConfigSchema>;
  psi: z.infer<typeof psiConfigSchema>;
};

export type ValidationResult<T> = {
  success: boolean;
  data?: T;
  errors?: Record<string, string>;
};

export type SlackConfigSchema = z.infer<typeof slackSchema>;
export type OpsGenieConfigSchema = z.infer<typeof opsGenieSchema>;
export type ConsoleConfigSchema = z.infer<typeof consoleSchema>;
export type CustomConfigSchema = z.infer<typeof customConfigSchema>;
export type GenAIConfigSchema = z.infer<typeof GenAIConfigSchema>;
export type PsiConfigSchema = z.infer<typeof psiConfigSchema>;
export type SpcConfigSchema = z.infer<typeof spcConfigSchema>;

export type CustomConfigParams = {
  schedule: string;
  sample: boolean;
  sample_size: number;
  dispatch_config: AlertDispatchConfig;
};

export type GenAIConfigParams = {
  schedule: string;
  sample_ratio: number;
  dispatch_config: AlertDispatchConfig;
};

export type PsiConfigParams = {
  schedule: string;
  threshold: PsiThreshold;
  dispatch_config: AlertDispatchConfig;
  features_to_monitor: string[];
};

export type SpcConfigParams = {
  schedule: string;
  sample: boolean;
  sample_size: number;
  rule: string;
  dispatch_config: AlertDispatchConfig;
  features_to_monitor: string[];
};

export type ConfigParams =
  | CustomConfigParams
  | PsiConfigParams
  | SpcConfigParams
  | GenAIConfigParams;

// Function to get appropriate params based on config type
export function getConfigParams(config: DriftConfigType): ConfigParams {
  if (isCustomConfig(config)) {
    return {
      schedule: config.alert_config.schedule,
      sample: config.sample,
      sample_size: config.sample_size,
      dispatch_config: config.alert_config.dispatch_config,
    };
  }

  if (isGenAIConfig(config)) {
    return {
      schedule: config.alert_config.schedule,
      sample_ratio: config.sample_ratio,
      dispatch_config: config.alert_config.dispatch_config,
    };
  }

  if (isPsiConfig(config)) {
    return {
      schedule: config.alert_config.schedule,
      threshold: config.alert_config.threshold,
      dispatch_config: config.alert_config.dispatch_config,
      features_to_monitor: config.alert_config.features_to_monitor,
    };
  }

  if (isSpcConfig(config)) {
    return {
      schedule: config.alert_config.schedule,
      sample: config.sample,
      sample_size: config.sample_size,
      rule: config.alert_config.rule.rule,
      dispatch_config: config.alert_config.dispatch_config,
      features_to_monitor: config.alert_config.features_to_monitor,
    };
  }

  throw new Error(`Unknown config type`);
}

export function validateSlack(
  channel: string
): ValidationResult<SlackConfigSchema> {
  try {
    const validData = slackSchema.parse({ channel });
    return {
      success: true,
      data: validData,
    };
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errors = error.errors.reduce<
        Record<keyof SlackConfigSchema, string>
      >((acc, curr) => {
        const path = curr.path[0] as keyof SlackConfigSchema;
        acc[path] = curr.message;
        return acc;
      }, {} as Record<keyof SlackConfigSchema, string>);

      return {
        success: false,
        errors,
      };
    }
    return {
      success: false,
      errors: { channel: "Unexpected validation error" },
    };
  }
}

export function validateConsole(
  enabled: boolean
): ValidationResult<ConsoleConfigSchema> {
  try {
    const validData = consoleSchema.parse({
      enabled: enabled,
    });
    return {
      success: true,
      data: validData,
    };
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errors = error.errors.reduce<
        Record<keyof ConsoleConfigSchema, string>
      >((acc, curr) => {
        const path = curr.path[0] as keyof ConsoleConfigSchema;
        acc[path] = curr.message;
        return acc;
      }, {} as Record<keyof ConsoleConfigSchema, string>);

      return {
        success: false,
        errors,
      };
    }
    return {
      success: false,
      errors: { enabled: "Unexpected validation error" },
    };
  }
}

export function validateOpsGenie(
  team: string,
  priority: string
): ValidationResult<OpsGenieConfigSchema> {
  try {
    const validData = opsGenieSchema.parse({ team, priority });
    return {
      success: true,
      data: validData,
    };
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errors = error.errors.reduce<
        Record<keyof OpsGenieConfigSchema, string>
      >((acc, curr) => {
        const path = curr.path[0] as keyof OpsGenieConfigSchema;
        acc[path] = curr.message;
        return acc;
      }, {} as Record<keyof OpsGenieConfigSchema, string>);

      return {
        success: false,
        errors,
      };
    }
    return {
      success: false,
      errors: {
        team: "Unexpected validation error",
        priority: "Unexpected validation error",
      },
    };
  }
}

export function validateCustomConfig(
  schedule: string,
  sample: boolean,
  sample_size: number
): ValidationResult<CustomConfigSchema> {
  try {
    const validData = customConfigSchema.parse({
      schedule,
      sample: sample,
      sample_size: Number(sample_size),
    });

    return {
      success: true,
      data: validData,
    };
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errors = error.errors.reduce<
        Record<keyof CustomConfigSchema, string>
      >((acc, curr) => {
        const path = curr.path[0] as keyof CustomConfigSchema;
        acc[path] = curr.message;
        return acc;
      }, {} as Record<keyof CustomConfigSchema, string>);

      return {
        success: false,
        errors,
      };
    }
    return {
      success: false,
      errors: {
        schedule: "Unexpected validation error",
        sample: "Unexpected validation error",
        sample_size: "Unexpected validation error",
      },
    };
  }
}

export function validateGenAIConfig(
  schedule: string,
  sample_ratio: number
): ValidationResult<GenAIConfigSchema> {
  try {
    const validData = z
      .object({
        schedule: z.string().default("0 0 0 * * *"),
        sample_ratio: z.coerce
          .number()
          .min(0, { message: "Value cannot be less than 0.0" })
          .max(1, {
            message: "Value cannot be greater than 1.0",
          }),
      })
      .parse({
        schedule,
        sample_rate: Number(sample_ratio),
      });

    return {
      success: true,
      data: validData,
    };
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errors = error.errors.reduce<
        Record<keyof GenAIConfigSchema, string>
      >((acc, curr) => {
        const path = curr.path[0] as keyof GenAIConfigSchema;
        acc[path] = curr.message;
        return acc;
      }, {} as Record<keyof GenAIConfigSchema, string>);

      return {
        success: false,
        errors,
      };
    }
    return {
      success: false,
      errors: {
        schedule: "Unexpected validation error",
        sample_ratio: "Unexpected validation error",
      },
    };
  }
}

export function validatePsiConfig(
  schedule: string,
  psi_threshold_value: number,
  psi_threshold_type: string,
  features_to_monitor: string[]
): ValidationResult<PsiConfigSchema> {
  try {
    const validData = psiConfigSchema.parse({
      schedule,
      psi_threshold_value,
      psi_threshold_type,
      features_to_monitor,
    });
    return {
      success: true,
      data: validData,
    };
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errors = error.errors.reduce<Record<keyof PsiConfigSchema, string>>(
        (acc, curr) => {
          const path = curr.path[0] as keyof PsiConfigSchema;
          acc[path] = curr.message;
          return acc;
        },
        {} as Record<keyof PsiConfigSchema, string>
      );

      return {
        success: false,
        errors,
      };
    }
    return {
      success: false,
      errors: {
        schedule: "Unexpected validation error",
        psi_threshold: "Unexpected validation error",
        features_to_monitor: "Unexpected validation error",
      },
    };
  }
}

export function validateSpcConfig(
  schedule: string,
  sample: boolean,
  sample_size: number,
  rule: string,
  features_to_monitor: string[]
): ValidationResult<SpcConfigSchema> {
  try {
    const validData = spcConfigSchema.parse({
      schedule,
      sample,
      sample_size,
      rule,
      features_to_monitor,
    });
    return {
      success: true,
      data: validData,
    };
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errors = error.errors.reduce<Record<keyof SpcConfigSchema, string>>(
        (acc, curr) => {
          const path = curr.path[0] as keyof SpcConfigSchema;
          acc[path] = curr.message;
          return acc;
        },
        {} as Record<keyof SpcConfigSchema, string>
      );

      return {
        success: false,
        errors,
      };
    }
    return {
      success: false,
      errors: {
        schedule: "Unexpected validation error",
        sample: "Unexpected validation error",
        sample_size: "Unexpected validation error",
        rule: "Unexpected validation error",
        features_to_monitor: "Unexpected validation error",
      },
    };
  }
}

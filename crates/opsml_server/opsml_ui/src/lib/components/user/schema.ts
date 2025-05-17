import { z } from "zod";

// Validation schema for login
export const useLoginSchema = z.object({
  username: z.string(),
  password: z.string(),
});

// Generic return for data or errors to be handled in UI
export type ValidationResult<T> = {
  success: boolean;
  data?: T;
  errors?: Record<string, string>;
};

export type UseLoginSchema = z.infer<typeof useLoginSchema>;

/**
 * Function to validate login schema
 * @param username - Username string
 * @param password - Password string
 * @returns ValidationResult object containing success status, data, or errors
 */
export function validateLoginSchema(
  username: string,
  password: string
): ValidationResult<UseLoginSchema> {
  let parsed = useLoginSchema.safeParse({ username, password });

  if (parsed.success) {
    return {
      success: true,
      data: parsed.data,
    };
  } else {
    let errors = parsed.error.errors.reduce<
      Record<keyof UseLoginSchema, string>
    >((acc, curr) => {
      const path = curr.path[0] as keyof UseLoginSchema;
      acc[path] = curr.message;
      return acc;
    }, {} as Record<keyof UseLoginSchema, string>);
    return {
      success: false,
      errors,
    };
  }
}

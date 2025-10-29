import { z } from "zod";

// Validation schema for login
export const useLoginSchema = z.object({
  username: z.string(),
  password: z.string(),
});

// Validation schema for creating/registering user
export const userRegisterSchema = z
  .object({
    email: z.string().email(),
    username: z.string(),
    password: z
      .string()
      .min(8, { message: "Password must be at least 8 characters long" })
      .max(32, { message: "Password cannot be longer than 32 characters" })
      .regex(/[A-Z]/, {
        message: "Password must contain at least one uppercase letter",
      })
      .regex(/[a-z]/, {
        message: "Password must contain at least one lowercase letter",
      })
      .regex(/[0-9]/, { message: "Password must contain at least one number" })
      .regex(/[^A-Za-z0-9\s]/, {
        message: "Password must contain at least one special character",
      }),
    reEnterPassword: z.string(),
  })
  .superRefine(({ reEnterPassword, password }, ctx) => {
    if (reEnterPassword !== password) {
      ctx.addIssue({
        code: "custom",
        message: "The passwords did not match",
        path: ["reEnterPassword"],
      });
    }
  });

export const emailSchema = z.string().email();

// Validation schema for resetting password
export const passwordResetSchema = z
  .object({
    username: z.string(),
    recoveryCode: z.string(),
    newPassword: z
      .string()
      .min(8, { message: "Password must be at least 8 characters long" })
      .max(32, { message: "Password cannot be longer than 32 characters" })
      .regex(/[A-Z]/, {
        message: "Password must contain at least one uppercase letter",
      })
      .regex(/[a-z]/, {
        message: "Password must contain at least one lowercase letter",
      })
      .regex(/[0-9]/, { message: "Password must contain at least one number" })
      .regex(/[^A-Za-z0-9\s]/, {
        message: "Password must contain at least one special character",
      }),
    confirmPassword: z.string(),
  })
  .superRefine(({ confirmPassword, newPassword }, ctx) => {
    if (confirmPassword !== newPassword) {
      ctx.addIssue({
        code: "custom",
        message: "The passwords did not match",
        path: ["confirmPassword"],
      });
    }
  });

// Generic return for data or errors to be handled in UI
export type ValidationResult<T> = {
  success: boolean;
  data?: T;
  errors?: Record<string, string>;
};

export type UseLoginSchema = z.infer<typeof useLoginSchema>;
export type UserRegisterSchema = z.infer<typeof userRegisterSchema>;
export type PasswordResetSchema = z.infer<typeof passwordResetSchema>;

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

/**
 * Function to validate user registration schema
 * @param username - Username string
 * @param password - Password string
 * @param email - Email string
 * @returns ValidationResult object containing success status, data, or errors
 */
export function validateUserRegisterSchema(
  username: string,
  password: string,
  reEnterPassword: string,
  email: string
): ValidationResult<UserRegisterSchema> {
  // if email is not provided, use username
  // this is for cases where a user wants to use their email address as a username
  if (!email) {
    email = username;
  }

  let parsed = userRegisterSchema.safeParse({
    email,
    username,
    password,
    reEnterPassword,
  });

  if (parsed.success) {
    return {
      success: true,
      data: parsed.data,
    };
  } else {
    let errors = parsed.error.errors.reduce<
      Record<keyof UserRegisterSchema, string>
    >((acc, curr) => {
      const path = curr.path[0] as keyof UserRegisterSchema;
      acc[path] = curr.message;
      return acc;
    }, {} as Record<keyof UserRegisterSchema, string>);
    return {
      success: false,
      errors,
    };
  }
}

/**
 * Function to validate password reset schema
 * @param username - Username string
 * @param recovery_code - Recovery code string
 * @param new_password - New password string
 * @returns ValidationResult object containing success status, data, or errors
 */
export function validatePasswordResetSchema(
  username: string,
  recoveryCode: string,
  newPassword: string,
  confirmPassword: string
): ValidationResult<PasswordResetSchema> {
  let parsed = passwordResetSchema.safeParse({
    username,
    recoveryCode,
    newPassword,
    confirmPassword,
  });

  if (parsed.success) {
    return {
      success: true,
      data: parsed.data,
    };
  } else {
    let errors = parsed.error.errors.reduce<
      Record<keyof PasswordResetSchema, string>
    >((acc, curr) => {
      const path = curr.path[0] as keyof PasswordResetSchema;
      acc[path] = curr.message;
      return acc;
    }, {} as Record<keyof PasswordResetSchema, string>);
    return {
      success: false,
      errors,
    };
  }
}

import type { CustomThemeConfig } from "@skeletonlabs/tw-plugin";

export const opsmlTheme: CustomThemeConfig = {
  name: "opsml",
  properties: {
    // =~= Theme Properties =~=
    "--theme-font-family-base": `Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji'`,
    "--theme-font-family-heading": `Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji'`,
    "--theme-font-color-base": "0 0 0",
    "--theme-font-color-dark": "255 255 255",
    "--theme-rounded-base": "9999px",
    "--theme-rounded-container": "8px",
    "--theme-border-base": "1px",
    // =~= Theme On-X Colors =~=
    "--on-primary": "255 255 255",
    "--on-secondary": "0 0 0",
    "--on-tertiary": "0 0 0",
    "--on-success": "0 0 0",
    "--on-warning": "0 0 0",
    "--on-error": "255 255 255",
    "--on-surface": "255 255 255",
    // =~= Theme Colors  =~=
    // primary | #4b3978
    "--color-primary-50": "228 225 235", // #e4e1eb
    "--color-primary-100": "219 215 228", // #dbd7e4
    "--color-primary-200": "210 206 221", // #d2cedd
    "--color-primary-300": "183 176 201", // #b7b0c9
    "--color-primary-400": "129 116 161", // #8174a1
    "--color-primary-500": "75 57 120", // #4b3978
    "--color-primary-600": "68 51 108", // #44336c
    "--color-primary-700": "56 43 90", // #382b5a
    "--color-primary-800": "45 34 72", // #2d2248
    "--color-primary-900": "37 28 59", // #251c3b
    // secondary | #04cd9b
    "--color-secondary-50": "217 248 240", // #d9f8f0
    "--color-secondary-100": "205 245 235", // #cdf5eb
    "--color-secondary-200": "192 243 230", // #c0f3e6
    "--color-secondary-300": "155 235 215", // #9bebd7
    "--color-secondary-400": "79 220 185", // #4fdcb9
    "--color-secondary-500": "4 205 155", // #04cd9b
    "--color-secondary-600": "4 185 140", // #04b98c
    "--color-secondary-700": "3 154 116", // #039a74
    "--color-secondary-800": "2 123 93", // #027b5d
    "--color-secondary-900": "2 100 76", // #02644c
    // tertiary | #b4a7d5
    "--color-tertiary-50": "244 242 249", // #f4f2f9
    "--color-tertiary-100": "240 237 247", // #f0edf7
    "--color-tertiary-200": "236 233 245", // #ece9f5
    "--color-tertiary-300": "225 220 238", // #e1dcee
    "--color-tertiary-400": "203 193 226", // #cbc1e2
    "--color-tertiary-500": "180 167 213", // #b4a7d5
    "--color-tertiary-600": "162 150 192", // #a296c0
    "--color-tertiary-700": "135 125 160", // #877da0
    "--color-tertiary-800": "108 100 128", // #6c6480
    "--color-tertiary-900": "88 82 104", // #585268
    // success | #1affa3
    "--color-success-50": "221 255 241", // #ddfff1
    "--color-success-100": "209 255 237", // #d1ffed
    "--color-success-200": "198 255 232", // #c6ffe8
    "--color-success-300": "163 255 218", // #a3ffda
    "--color-success-400": "95 255 191", // #5fffbf
    "--color-success-500": "26 255 163", // #1affa3
    "--color-success-600": "23 230 147", // #17e693
    "--color-success-700": "20 191 122", // #14bf7a
    "--color-success-800": "16 153 98", // #109962
    "--color-success-900": "13 125 80", // #0d7d50
    // warning | #6dc6fd
    "--color-warning-50": "233 246 255", // #e9f6ff
    "--color-warning-100": "226 244 255", // #e2f4ff
    "--color-warning-200": "219 241 255", // #dbf1ff
    "--color-warning-300": "197 232 254", // #c5e8fe
    "--color-warning-400": "153 215 254", // #99d7fe
    "--color-warning-500": "109 198 253", // #6dc6fd
    "--color-warning-600": "98 178 228", // #62b2e4
    "--color-warning-700": "82 149 190", // #5295be
    "--color-warning-800": "65 119 152", // #417798
    "--color-warning-900": "53 97 124", // #35617c
    // error | #D41976
    "--color-error-50": "249 221 234", // #f9ddea
    "--color-error-100": "246 209 228", // #f6d1e4
    "--color-error-200": "244 198 221", // #f4c6dd
    "--color-error-300": "238 163 200", // #eea3c8
    "--color-error-400": "225 94 159", // #e15e9f
    "--color-error-500": "212 25 118", // #D41976
    "--color-error-600": "191 23 106", // #bf176a
    "--color-error-700": "159 19 89", // #9f1359
    "--color-error-800": "127 15 71", // #7f0f47
    "--color-error-900": "104 12 58", // #680c3a

    // surface | #5e498f
    "--color-surface-50": "252 252 252", // #fcfcfc
    "--color-surface-100": "244 244 244", // #f4f4f4
    "--color-surface-200": "241 241 241", // #f1f1f1
    "--color-surface-300": "233 233 233", // #e9e9e9
    "--color-surface-400": "216 216 216", // #d8d8d8
    "--color-surface-500": "94 73 143", // #5e498f
    "--color-surface-600": "85 66 129", // #554281
    "--color-surface-700": "71 55 107", // #47376b
    "--color-surface-800": "56 44 86", // #382c56
    "--color-surface-900": "46 36 70", // #2e2446
  },
};

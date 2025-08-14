"use client";

interface ErrorBannerProps {
  message: string | null;
}

export default function ErrorBanner({ message }: ErrorBannerProps) {
  if (!message) return null;
  return (
    <div
      role="alert"
      className="bg-red-100 text-red-700 border border-red-300 rounded p-2"
    >
      {message}
    </div>
  );
}

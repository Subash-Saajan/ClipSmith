"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const API_URL = "http://localhost:3000";

interface Clip {
  id: string;
  title: string;
  startTime: number;
  endTime: number;
  duration: number;
  url: string | null;
}

interface Job {
  id: string;
  youtubeUrl: string;
  prompt: string;
  jobType: "CLIP" | "GENERATE";
  status: string;
  progress: number;
  errorMessage: string | null;
  createdAt: string;
  clips: Clip[];
}

export default function Home() {
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [jobs, setJobs] = useState<Job[]>([]);

  // Fetch jobs on load and periodically
  // Poll faster (3s) when jobs are processing, slower (10s) otherwise
  useEffect(() => {
    fetchJobs();
    const hasActiveJobs = jobs.some((job) =>
      !["COMPLETED", "FAILED"].includes(job.status)
    );
    const interval = setInterval(fetchJobs, hasActiveJobs ? 3000 : 10000);
    return () => clearInterval(interval);
  }, [jobs.length, jobs.map(j => j.status).join(",")]);

  const fetchJobs = async () => {
    try {
      const res = await fetch(`${API_URL}/jobs`);
      const data = await res.json();
      setJobs(data);
    } catch (error) {
      console.error("Failed to fetch jobs:", error);
    }
  };

  const handleSubmit = async (selectedJobType: "CLIP" | "GENERATE") => {
    if (!youtubeUrl) return;

    setLoading(true);
    try {
      const defaultPrompt = selectedJobType === "CLIP"
        ? "Find the most interesting and engaging moments"
        : "Generate a similar style video";

      const res = await fetch(`${API_URL}/jobs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          youtubeUrl,
          prompt: prompt || defaultPrompt,
          jobType: selectedJobType,
        }),
      });

      if (res.ok) {
        setYoutubeUrl("");
        setPrompt("");
        fetchJobs();
      }
    } catch (error) {
      console.error("Failed to create job:", error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "COMPLETED":
        return "text-green-500";
      case "FAILED":
        return "text-red-500";
      case "PENDING":
        return "text-zinc-500";
      default:
        return "text-blue-400";
    }
  };

  // Steps for CLIP job type
  const clipSteps = [
    { key: "PENDING", label: "Queue", icon: "⏳" },
    { key: "DOWNLOADING", label: "Download", icon: "⬇️" },
    { key: "TRANSCRIBING", label: "Transcribe", icon: "🎤" },
    { key: "ANALYZING", label: "Analyze", icon: "🤖" },
    { key: "CLIPPING", label: "Clip", icon: "✂️" },
    { key: "COMPLETED", label: "Done", icon: "✅" },
  ];

  // Steps for GENERATE job type
  const generateSteps = [
    { key: "PENDING", label: "Queue", icon: "⏳" },
    { key: "DOWNLOADING", label: "Download", icon: "⬇️" },
    { key: "GENERATING", label: "AI Generate", icon: "🎬" },
    { key: "COMPLETED", label: "Done", icon: "✅" },
  ];

  const getStepsForJob = (job: Job) => {
    return job.jobType === "GENERATE" ? generateSteps : clipSteps;
  };

  const getStepStatus = (stepKey: string, currentStatus: string, steps: typeof clipSteps) => {
    const stepIndex = steps.findIndex((s) => s.key === stepKey);
    const currentIndex = steps.findIndex((s) => s.key === currentStatus);

    if (currentStatus === "FAILED") return "failed";
    if (stepIndex < currentIndex) return "completed";
    if (stepIndex === currentIndex) return "active";
    return "pending";
  };

  
  return (
    <div className="min-h-screen bg-zinc-950 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-2">ClipForge</h1>
        <p className="text-zinc-400 mb-8">
          Extract viral clips from YouTube videos using AI
        </p>

        {/* Submit Form */}
        <Card className="bg-zinc-900 border-zinc-800 mb-8">
          <CardHeader>
            <CardTitle className="text-white">Create New Video</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-zinc-400 mb-2">
                  YouTube URL
                </label>
                <Input
                  type="url"
                  placeholder="https://www.youtube.com/watch?v=... or Shorts URL"
                  value={youtubeUrl}
                  onChange={(e) => setYoutubeUrl(e.target.value)}
                  className="bg-zinc-800 border-zinc-700 text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-zinc-400 mb-2">
                  Prompt (optional)
                </label>
                <Textarea
                  placeholder="Find the funniest moments, key insights, viral hooks..."
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  className="bg-zinc-800 border-zinc-700 text-white"
                  rows={3}
                />
              </div>

              {/* Single Clip button */}
              <Button
                type="button"
                onClick={() => handleSubmit("CLIP")}
                disabled={loading || !youtubeUrl}
                className="w-full bg-blue-600 hover:bg-blue-700 flex items-center justify-center gap-2"
              >
                <span>✂️</span>
                {loading ? "Processing..." : "Extract Viral Clips"}
              </Button>
              <p className="text-xs text-zinc-500 text-center">
                AI analyzes video content to find the most engaging moments
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Jobs List */}
        <h2 className="text-2xl font-semibold mb-4">Your Jobs</h2>
        {jobs.length === 0 ? (
          <p className="text-zinc-500">No jobs yet. Submit a YouTube URL to get started!</p>
        ) : (
          <div className="space-y-4">
            {jobs.map((job) => (
              <Card key={job.id} className="bg-zinc-900 border-zinc-800">
                <CardContent className="pt-6">
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`text-xs px-2 py-0.5 rounded ${
                          job.jobType === "GENERATE"
                            ? "bg-purple-600/30 text-purple-400"
                            : "bg-blue-600/30 text-blue-400"
                        }`}>
                          {job.jobType === "GENERATE" ? "🎬 Generate" : "✂️ Clip"}
                        </span>
                      </div>
                      <p className="text-sm text-zinc-400 truncate">
                        {job.youtubeUrl}
                      </p>
                      <p className="text-sm text-zinc-500 mt-1">
                        {job.prompt}
                      </p>
                    </div>
                    <span
                      className={`text-sm font-medium ${getStatusColor(
                        job.status
                      )}`}
                    >
                      {job.status}
                    </span>
                  </div>

                  {/* Step-by-step progress */}
                  {job.status !== "COMPLETED" && job.status !== "FAILED" && (() => {
                    const steps = getStepsForJob(job);
                    return (
                    <div className="mt-4 mb-4">
                      <div className="flex items-center justify-between">
                        {steps.map((step, index) => {
                          const status = getStepStatus(step.key, job.status, steps);
                          return (
                            <div key={step.key} className="flex items-center flex-1">
                              {/* Step circle */}
                              <div className="flex flex-col items-center">
                                <div
                                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm transition-all duration-300 ${
                                    status === "completed"
                                      ? "bg-green-600 text-white"
                                      : status === "active"
                                      ? job.jobType === "GENERATE" ? "bg-purple-600 text-white animate-pulse" : "bg-blue-600 text-white animate-pulse"
                                      : "bg-zinc-800 text-zinc-500"
                                  }`}
                                >
                                  {status === "completed" ? "✓" : step.icon}
                                </div>
                                <span
                                  className={`text-xs mt-1 ${
                                    status === "active"
                                      ? job.jobType === "GENERATE" ? "text-purple-400" : "text-blue-400"
                                      : status === "completed"
                                      ? "text-green-400"
                                      : "text-zinc-600"
                                  }`}
                                >
                                  {step.label}
                                </span>
                              </div>
                              {/* Connector line */}
                              {index < steps.length - 1 && (
                                <div
                                  className={`flex-1 h-0.5 mx-2 transition-all duration-300 ${
                                    status === "completed" ? "bg-green-600" : "bg-zinc-800"
                                  }`}
                                />
                              )}
                            </div>
                          );
                        })}
                      </div>
                      {/* Progress bar */}
                      <div className="mt-4">
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-xs text-zinc-400">
                            {job.status === "DOWNLOADING" && "Downloading video..."}
                            {job.status === "TRANSCRIBING" && "Transcribing audio..."}
                            {job.status === "ANALYZING" && "AI analyzing transcript..."}
                            {job.status === "CLIPPING" && "Creating clips..."}
                            {job.status === "GENERATING" && "AI generating new video..."}
                            {job.status === "PENDING" && "Waiting in queue..."}
                          </span>
                          <span className={`text-xs font-medium ${job.jobType === "GENERATE" ? "text-purple-400" : "text-blue-400"}`}>
                            {job.progress || 0}%
                          </span>
                        </div>
                        <div className="w-full h-2 bg-zinc-800 rounded-full overflow-hidden">
                          <div
                            className={`h-full transition-all duration-500 ease-out ${
                              job.jobType === "GENERATE"
                                ? "bg-gradient-to-r from-purple-600 to-purple-400"
                                : "bg-gradient-to-r from-blue-600 to-blue-400"
                            }`}
                            style={{ width: `${job.progress || 0}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  );})()}

                  {/* Show error message if job failed */}
                  {job.status === "FAILED" && job.errorMessage && (
                    <div className="mt-4 p-3 bg-red-900/30 border border-red-800 rounded-lg">
                      <p className="text-sm text-red-400 font-medium">Error:</p>
                      <p className="text-sm text-red-300 mt-1 break-all">
                        {job.errorMessage}
                      </p>
                    </div>
                  )}

                  {job.clips && job.clips.length > 0 && (
                    <div className="mt-4">
                      <p className="text-sm text-zinc-400 mb-2">
                        Generated Clips ({job.clips.length})
                      </p>
                      <div className="grid gap-2">
                        {job.clips.map((clip) => (
                          <div
                            key={clip.id}
                            className="bg-zinc-800 p-3 rounded-lg"
                          >
                            <p className="font-medium text-white">
                              {clip.title || "Untitled Clip"}
                            </p>
                            <p className="text-sm text-zinc-400">
                              {clip.startTime.toFixed(1)}s - {clip.endTime.toFixed(1)}s
                              ({clip.duration.toFixed(1)}s)
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <p className="text-xs text-zinc-600 mt-4">
                    {new Date(job.createdAt).toLocaleString()}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

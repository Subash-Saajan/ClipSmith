"use client";

import { Sparkles, Youtube, Moon, User, Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";

export default function DashboardPage() {
    const sampleClips = [
        { id: 1, title: "Funny Moment #1", duration: "0:45", thumbnail: "" },
        { id: 2, title: "Key Insight #2", duration: "1:12", thumbnail: "" },
        { id: 3, title: "Tutorial Segment #3", duration: "2:34", thumbnail: "" },
        { id: 4, title: "Product Demo #4", duration: "0:58", thumbnail: "" },
        { id: 5, title: "Reaction Clip #5", duration: "1:05", thumbnail: "" },
        { id: 6, title: "Highlight #6", duration: "0:32", thumbnail: "" },
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50">
            {/* Navigation Bar */}
            <nav className="border-b border-gray-200/50 glass sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-8">
                            <Link href="/" className="flex items-center gap-2">
                                <div className="w-8 h-8 bg-gradient-to-br from-primary to-primary-600 rounded-lg flex items-center justify-center">
                                    <Sparkles className="w-5 h-5 text-white" />
                                </div>
                                <span className="text-xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
                                    ClipSmith
                                </span>
                            </Link>

                            <div className="hidden md:flex items-center gap-6">
                                <Link href="/dashboard" className="text-sm font-semibold text-primary">
                                    Dashboard
                                </Link>
                                <Link href="#" className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">
                                    History
                                </Link>
                                <Link href="#" className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">
                                    Account
                                </Link>
                            </div>
                        </div>

                        <div className="flex items-center gap-4">
                            <Button variant="ghost" size="icon">
                                <Moon className="w-5 h-5" />
                            </Button>
                            <div className="w-10 h-10 bg-gradient-to-br from-primary to-primary-600 rounded-full flex items-center justify-center cursor-pointer hover:scale-105 transition-transform">
                                <User className="w-5 h-5 text-white" />
                            </div>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-6 py-12">
                {/* Input Card */}
                <div className="max-w-4xl mx-auto mb-12">
                    <Card className="glass border-2 shadow-xl">
                        <CardHeader>
                            <CardTitle className="text-2xl font-bold">Create New Clips</CardTitle>
                            <p className="text-gray-600 text-sm mt-2">
                                Paste a YouTube link and describe what clips you want to extract
                            </p>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="relative">
                                <Youtube className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-primary" />
                                <Input
                                    placeholder="Paste YouTube video link here..."
                                    className="pl-12 h-12"
                                />
                            </div>
                            <Textarea
                                placeholder="Describe the type of clips you want... (e.g., 'Extract funny moments', 'Get clips about productivity tips', 'Find all the key insights')"
                                className="min-h-[120px]"
                            />
                            <Button size="lg" className="w-full">
                                <Sparkles className="w-5 h-5 mr-2" />
                                Generate Clips
                            </Button>
                        </CardContent>
                    </Card>
                </div>

                {/* Status Component */}
                <div className="max-w-4xl mx-auto mb-12">
                    <div className="glass rounded-xl p-6 border border-gray-200">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="font-semibold text-lg">Processing Status</h3>
                            <Badge variant="success">Completed</Badge>
                        </div>
                        <div className="space-y-3">
                            <div className="flex items-center gap-3">
                                <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                </div>
                                <div className="flex-1">
                                    <p className="text-sm font-medium">Video analyzed</p>
                                    <p className="text-xs text-gray-500">Completed</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-3">
                                <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                </div>
                                <div className="flex-1">
                                    <p className="text-sm font-medium">AI processing</p>
                                    <p className="text-xs text-gray-500">Completed</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-3">
                                <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                </div>
                                <div className="flex-1">
                                    <p className="text-sm font-medium">Clips generated</p>
                                    <p className="text-xs text-gray-500">6 clips ready</p>
                                </div>
                            </div>
                        </div>

                        {/* Progress Bar */}
                        <div className="mt-4">
                            <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                                <div className="bg-gradient-to-r from-primary to-primary-600 h-full rounded-full" style={{ width: "100%" }}></div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Output Clips Grid */}
                <div>
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-2xl font-bold">Your Clips</h2>
                        <p className="text-gray-600">{sampleClips.length} clips generated</p>
                    </div>

                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {sampleClips.map((clip) => (
                            <Card key={clip.id} className="border-2 hover:border-primary/50 hover:shadow-xl transition-all group cursor-pointer">
                                {/* Thumbnail */}
                                <div className="relative aspect-video bg-gradient-to-br from-gray-900 to-gray-800 rounded-t-xl overflow-hidden">
                                    <div className="absolute inset-0 flex items-center justify-center">
                                        <div className="w-12 h-12 bg-white/10 backdrop-blur-sm rounded-full flex items-center justify-center group-hover:scale-110 transition-transform">
                                            <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                                                <path d="M8 5v14l11-7z" />
                                            </svg>
                                        </div>
                                    </div>
                                    <div className="absolute top-3 right-3">
                                        <Badge variant="secondary" className="bg-black/60 text-white border-0">
                                            {clip.duration}
                                        </Badge>
                                    </div>
                                </div>

                                {/* Card Content */}
                                <CardContent className="p-4">
                                    <h3 className="font-semibold mb-3 group-hover:text-primary transition-colors">
                                        {clip.title}
                                    </h3>
                                    <Button variant="outline" className="w-full group-hover:bg-primary group-hover:text-white group-hover:border-primary">
                                        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                        </svg>
                                        Download
                                    </Button>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </div>

                {/* Empty State (hidden when clips exist) */}
                {sampleClips.length === 0 && (
                    <div className="max-w-2xl mx-auto text-center py-16">
                        <div className="w-20 h-20 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                            <Sparkles className="w-10 h-10 text-gray-400" />
                        </div>
                        <h3 className="text-2xl font-bold mb-2">No clips yet</h3>
                        <p className="text-gray-600 mb-6">
                            Generate your first set of clips by pasting a YouTube link above
                        </p>
                    </div>
                )}
            </main>
        </div>
    );
}

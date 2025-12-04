"use client";

import { Sparkles, Zap, Globe, Download, Check, Youtube, Moon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";

export default function LandingPage() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50">
            {/* Navigation */}
            <nav className="border-b border-gray-200/50 glass sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <div className="w-8 h-8 bg-gradient-to-br from-primary to-primary-600 rounded-lg flex items-center justify-center">
                                <Sparkles className="w-5 h-5 text-white" />
                            </div>
                            <span className="text-xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
                                ClipSmith
                            </span>
                        </div>
                        <div className="hidden md:flex items-center gap-8">
                            <Link href="#features" className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">
                                Features
                            </Link>
                            <Link href="#pricing" className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">
                                Pricing
                            </Link>
                            <Link href="/dashboard" className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">
                                Dashboard
                            </Link>
                            <Button variant="ghost" size="icon">
                                <Moon className="w-5 h-5" />
                            </Button>
                            <Button size="sm">Get Started</Button>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="relative py-24 md:py-32 overflow-hidden">
                <div className="absolute inset-0 bg-grid-gray-900/[0.02] bg-[size:32px_32px]" />
                <div className="max-w-7xl mx-auto px-6 relative">
                    <div className="text-center max-w-4xl mx-auto mb-16 animate-fade-in">
                        <Badge className="mb-6 text-xs px-4 py-1.5">
                            <Sparkles className="w-3 h-3 mr-1" />
                            AI-Powered Video Clipping
                        </Badge>
                        <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-gray-900 via-gray-800 to-gray-600 bg-clip-text text-transparent leading-tight">
                            Convert YouTube Videos into Viral Clips with AI
                        </h1>
                        <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto leading-relaxed">
                            Transform your long-form content into engaging short clips automatically. Perfect for TikTok, Instagram Reels, and YouTube Shorts.
                        </p>

                        {/* Input Mock UI */}
                        <div className="glass rounded-2xl p-8 shadow-2xl shadow-primary/10 max-w-3xl mx-auto mb-8 animate-slide-up">
                            <div className="space-y-4">
                                <div className="relative">
                                    <Youtube className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                                    <Input
                                        placeholder="Paste YouTube video link here..."
                                        className="pl-12 h-12 text-base"
                                    />
                                </div>
                                <Textarea
                                    placeholder="Describe the type of clips you want... (e.g., 'Extract funny moments', 'Get clips about productivity tips')"
                                    className="min-h-[100px]"
                                />
                                <Button size="lg" className="w-full text-base font-semibold">
                                    <Sparkles className="w-5 h-5 mr-2" />
                                    Generate Clips
                                </Button>
                            </div>
                        </div>

                        <div className="flex items-center justify-center gap-4">
                            <Link href="/dashboard">
                                <Button size="lg">
                                    Get Started
                                </Button>
                            </Link>
                            <Button size="lg" variant="outline">
                                <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M8 5v14l11-7z" />
                                </svg>
                                Watch Demo
                            </Button>
                        </div>
                    </div>

                    {/* Dashboard Preview */}
                    <div className="max-w-6xl mx-auto animate-scale-in">
                        <div className="relative">
                            <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-purple-500/20 blur-3xl" />
                            <div className="relative glass rounded-2xl p-2 shadow-2xl">
                                <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-8 aspect-video flex items-center justify-center">
                                    <div className="text-center">
                                        <div className="w-16 h-16 bg-primary/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                                            <Sparkles className="w-8 h-8 text-primary" />
                                        </div>
                                        <p className="text-gray-400 text-sm">Dashboard Preview</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section id="features" className="py-24 bg-white">
                <div className="max-w-7xl mx-auto px-6">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl md:text-5xl font-bold mb-4">Everything you need to go viral</h2>
                        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                            Powerful AI tools to transform your content into shareable moments
                        </p>
                    </div>

                    <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
                        <Card className="border-2 hover:border-primary/50 hover:shadow-xl transition-all group">
                            <CardHeader>
                                <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                    <Zap className="w-6 h-6 text-primary" />
                                </div>
                                <CardTitle className="text-xl">Automatic Clipping</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <p className="text-gray-600">
                                    AI identifies the best moments in your videos automatically
                                </p>
                            </CardContent>
                        </Card>

                        <Card className="border-2 hover:border-primary/50 hover:shadow-xl transition-all group">
                            <CardHeader>
                                <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                    <Sparkles className="w-6 h-6 text-primary" />
                                </div>
                                <CardTitle className="text-xl">AI Understanding</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <p className="text-gray-600">
                                    Understands context and extracts clips based on your prompts
                                </p>
                            </CardContent>
                        </Card>

                        <Card className="border-2 hover:border-primary/50 hover:shadow-xl transition-all group">
                            <CardHeader>
                                <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                    <Globe className="w-6 h-6 text-primary" />
                                </div>
                                <CardTitle className="text-xl">Multi-Platform Formats</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <p className="text-gray-600">
                                    Optimized for TikTok, Instagram Reels, and YouTube Shorts
                                </p>
                            </CardContent>
                        </Card>

                        <Card className="border-2 hover:border-primary/50 hover:shadow-xl transition-all group">
                            <CardHeader>
                                <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                    <Download className="w-6 h-6 text-primary" />
                                </div>
                                <CardTitle className="text-xl">Export Ready</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <p className="text-gray-600">
                                    Download clips ready to upload with proper formatting
                                </p>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </section>

            {/* Pricing Section */}
            <section id="pricing" className="py-24 bg-gradient-to-br from-gray-50 to-white">
                <div className="max-w-7xl mx-auto px-6">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl md:text-5xl font-bold mb-4">Simple, transparent pricing</h2>
                        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                            Choose the plan that works for you
                        </p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
                        {/* Free Plan */}
                        <Card className="border-2">
                            <CardHeader>
                                <CardTitle className="text-2xl">Free</CardTitle>
                                <CardDescription className="text-base">Perfect for trying out</CardDescription>
                                <div className="pt-4">
                                    <span className="text-4xl font-bold">$0</span>
                                    <span className="text-gray-600">/month</span>
                                </div>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <ul className="space-y-3">
                                    <li className="flex items-center gap-2">
                                        <Check className="w-5 h-5 text-primary" />
                                        <span className="text-gray-600">5 clips per month</span>
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <Check className="w-5 h-5 text-primary" />
                                        <span className="text-gray-600">720p quality</span>
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <Check className="w-5 h-5 text-primary" />
                                        <span className="text-gray-600">Basic AI clipping</span>
                                    </li>
                                </ul>
                            </CardContent>
                            <CardFooter>
                                <Button variant="outline" className="w-full">Get Started</Button>
                            </CardFooter>
                        </Card>

                        {/* Pro Plan */}
                        <Card className="border-2 border-primary shadow-xl shadow-primary/20 relative">
                            <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                                <Badge className="px-4 py-1">Most Popular</Badge>
                            </div>
                            <CardHeader>
                                <CardTitle className="text-2xl">Pro</CardTitle>
                                <CardDescription className="text-base">For content creators</CardDescription>
                                <div className="pt-4">
                                    <span className="text-4xl font-bold">$29</span>
                                    <span className="text-gray-600">/month</span>
                                </div>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <ul className="space-y-3">
                                    <li className="flex items-center gap-2">
                                        <Check className="w-5 h-5 text-primary" />
                                        <span className="text-gray-600">Unlimited clips</span>
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <Check className="w-5 h-5 text-primary" />
                                        <span className="text-gray-600">1080p quality</span>
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <Check className="w-5 h-5 text-primary" />
                                        <span className="text-gray-600">Advanced AI features</span>
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <Check className="w-5 h-5 text-primary" />
                                        <span className="text-gray-600">Priority support</span>
                                    </li>
                                </ul>
                            </CardContent>
                            <CardFooter>
                                <Button className="w-full">Get Started</Button>
                            </CardFooter>
                        </Card>

                        {/* Enterprise Plan */}
                        <Card className="border-2">
                            <CardHeader>
                                <CardTitle className="text-2xl">Enterprise</CardTitle>
                                <CardDescription className="text-base">For teams and agencies</CardDescription>
                                <div className="pt-4">
                                    <span className="text-4xl font-bold">$99</span>
                                    <span className="text-gray-600">/month</span>
                                </div>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <ul className="space-y-3">
                                    <li className="flex items-center gap-2">
                                        <Check className="w-5 h-5 text-primary" />
                                        <span className="text-gray-600">Unlimited clips</span>
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <Check className="w-5 h-5 text-primary" />
                                        <span className="text-gray-600">4K quality</span>
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <Check className="w-5 h-5 text-primary" />
                                        <span className="text-gray-600">Custom AI models</span>
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <Check className="w-5 h-5 text-primary" />
                                        <span className="text-gray-600">Dedicated support</span>
                                    </li>
                                </ul>
                            </CardContent>
                            <CardFooter>
                                <Button variant="outline" className="w-full">Contact Sales</Button>
                            </CardFooter>
                        </Card>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="border-t border-gray-200 bg-white py-12">
                <div className="max-w-7xl mx-auto px-6">
                    <div className="grid md:grid-cols-4 gap-8 mb-8">
                        <div>
                            <div className="flex items-center gap-2 mb-4">
                                <div className="w-8 h-8 bg-gradient-to-br from-primary to-primary-600 rounded-lg flex items-center justify-center">
                                    <Sparkles className="w-5 h-5 text-white" />
                                </div>
                                <span className="text-xl font-bold">ClipSmith</span>
                            </div>
                            <p className="text-gray-600 text-sm">
                                Transform your videos into viral clips with AI
                            </p>
                        </div>

                        <div>
                            <h4 className="font-semibold mb-4">Product</h4>
                            <ul className="space-y-2 text-sm text-gray-600">
                                <li><Link href="#features" className="hover:text-gray-900">Features</Link></li>
                                <li><Link href="#pricing" className="hover:text-gray-900">Pricing</Link></li>
                                <li><Link href="/dashboard" className="hover:text-gray-900">Dashboard</Link></li>
                            </ul>
                        </div>

                        <div>
                            <h4 className="font-semibold mb-4">Company</h4>
                            <ul className="space-y-2 text-sm text-gray-600">
                                <li><Link href="#" className="hover:text-gray-900">About</Link></li>
                                <li><Link href="#" className="hover:text-gray-900">Blog</Link></li>
                                <li><Link href="#" className="hover:text-gray-900">Contact</Link></li>
                            </ul>
                        </div>

                        <div>
                            <h4 className="font-semibold mb-4">Connect</h4>
                            <div className="flex gap-4">
                                <Link href="#" className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center hover:bg-gray-200 transition-colors">
                                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M23 3a10.9 10.9 0 01-3.14 1.53 4.48 4.48 0 00-7.86 3v1A10.66 10.66 0 013 4s-4 9 5 13a11.64 11.64 0 01-7 2c9 5 20 0 20-11.5a4.5 4.5 0 00-.08-.83A7.72 7.72 0 0023 3z" /></svg>
                                </Link>
                                <Link href="#" className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center hover:bg-gray-200 transition-colors">
                                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" /></svg>
                                </Link>
                                <Link href="#" className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center hover:bg-gray-200 transition-colors">
                                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" /></svg>
                                </Link>
                            </div>
                        </div>
                    </div>

                    <div className="border-t border-gray-200 pt-8">
                        <p className="text-center text-sm text-gray-600">
                            © 2024 ClipSmith. All rights reserved.
                        </p>
                    </div>
                </div>
            </footer>
        </div>
    );
}

import { Injectable } from '@nestjs/common';
import { InjectQueue } from '@nestjs/bullmq';
import { Queue } from 'bullmq';
import { PrismaService } from '../prisma/prisma.service';
import { CreateJobDto } from './dto/create-job.dto';
import { CLIP_QUEUE } from '../queue/queue.module';

@Injectable()
export class JobsService {
  constructor(
    private prisma: PrismaService,
    @InjectQueue(CLIP_QUEUE) private clipQueue: Queue,
  ) {}

  async create(createJobDto: CreateJobDto) {
    const jobType = createJobDto.jobType || 'CLIP';

    // Create job in database
    const job = await this.prisma.job.create({
      data: {
        youtubeUrl: createJobDto.youtubeUrl,
        prompt: createJobDto.prompt,
        jobType: jobType,
        status: 'PENDING',
      },
    });

    // Add job to queue for processing
    // Include jobType so worker knows which pipeline to use
    await this.clipQueue.add('process-clip', {
      id: job.id,
      youtubeUrl: job.youtubeUrl,
      prompt: job.prompt,
      jobType: jobType,
    });

    return job;
  }

  async findAll() {
    return this.prisma.job.findMany({
      include: { clips: true },
      orderBy: { createdAt: 'desc' },
    });
  }

  async findOne(id: string) {
    return this.prisma.job.findUnique({
      where: { id },
      include: { clips: true },
    });
  }
}

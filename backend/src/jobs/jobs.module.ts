import { Module } from '@nestjs/common';
import { BullModule } from '@nestjs/bullmq';
import { JobsController } from './jobs.controller';
import { JobsService } from './jobs.service';
import { CLIP_QUEUE } from '../queue/queue.module';

@Module({
  imports: [
    BullModule.registerQueue({
      name: CLIP_QUEUE,
    }),
  ],
  controllers: [JobsController],
  providers: [JobsService],
})
export class JobsModule {}

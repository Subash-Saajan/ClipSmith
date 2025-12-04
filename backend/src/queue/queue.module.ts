import { Module } from '@nestjs/common';
import { BullModule } from '@nestjs/bullmq';

export const CLIP_QUEUE = 'clip-processing';

@Module({
  imports: [
    BullModule.registerQueue({
      name: CLIP_QUEUE,
    }),
  ],
  exports: [BullModule],
})
export class QueueModule {}

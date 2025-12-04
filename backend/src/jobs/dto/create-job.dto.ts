export class CreateJobDto {
  youtubeUrl: string;
  prompt: string;
  jobType?: 'CLIP' | 'GENERATE'; // Optional, defaults to CLIP
}

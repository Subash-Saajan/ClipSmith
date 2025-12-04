import { PrismaClient } from '@prisma/client';
import * as dotenv from 'dotenv';

dotenv.config();

const prisma = new PrismaClient();

async function clearAll() {
  const clips = await prisma.clip.deleteMany({});
  console.log('Deleted', clips.count, 'clips');

  const jobs = await prisma.job.deleteMany({});
  console.log('Deleted', jobs.count, 'jobs');

  await prisma.$disconnect();
}

clearAll();

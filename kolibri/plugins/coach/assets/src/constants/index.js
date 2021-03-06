import { LessonsPageNames } from './lessonsConstants';

export const PageNames = {
  REPORTS_PAGE: 'REPORTS_PAGE',
  PLAN_PAGE: 'PLAN_PAGE',
  NEW_COACH_PAGES: 'NEW_COACH_PAGES',
  EXAMS: 'EXAMS',
  EXAM_CREATION_ROOT: 'EXAM_CREATION_ROOT',
  EXAM_CREATION_TOPIC: 'EXAM_CREATION_TOPIC',
  EXAM_CREATION_PREVIEW: 'EXAM_CREATION_PREVIEW',
  EXAM_CREATION_SEARCH: 'EXAM_CREATION_SEARCH',
  EXAM_CREATION_QUESTION_SELECTION: 'EXAM_CREATION_QUESTION_SELECTION',
  EXAM_PREVIEW: 'EXAM_PREVIEW',
  EXAM_REPORT: 'EXAM_REPORT',
  EXAM_REPORT_DETAIL: 'EXAM_REPORT_DETAIL',
  EXAM_REPORT_DETAIL_ROOT: 'EXAM_REPORT_DETAIL_ROOT',
};

export const GroupModals = {
  CREATE_GROUP: 'CREATE_GROUP',
  RENAME_GROUP: 'RENAME_GROUP',
  DELETE_GROUP: 'DELETE_GROUP',
  MOVE_LEARNERS: 'MOVE_LEARNERS',
};

export const pageNameToModuleMap = {
  [PageNames.EXAMS]: 'examsRoot',
  [PageNames.EXAM_REPORT]: 'examReport',
  [PageNames.EXAM_REPORT_DETAIL]: 'examReportDetail',
  [LessonsPageNames.PLAN_LESSONS_ROOT]: 'lessonsRoot',
  [LessonsPageNames.RESOURCE_USER_REPORT]: 'exerciseDetail',
  // Omitting modules for resource selection, exam creation, and preview to prevent
  // default module state resetting behavior.
};

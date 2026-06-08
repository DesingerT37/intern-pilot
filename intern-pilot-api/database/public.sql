/*
 Navicat Premium Data Transfer

 Source Server         : 本地
 Source Server Type    : PostgreSQL
 Source Server Version : 170010 (170010)
 Source Host           : localhost:5432
 Source Catalog        : internpilot
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 170010 (170010)
 File Encoding         : 65001

 Date: 08/06/2026 18:26:29
*/


-- ----------------------------
-- Type structure for gtrgm
-- ----------------------------
DROP TYPE IF EXISTS "public"."gtrgm";
CREATE TYPE "public"."gtrgm" (
  INPUT = "public"."gtrgm_in",
  OUTPUT = "public"."gtrgm_out",
  INTERNALLENGTH = VARIABLE,
  CATEGORY = U,
  DELIMITER = ','
);
ALTER TYPE "public"."gtrgm" OWNER TO "postgres";

-- ----------------------------
-- Sequence structure for batch_analyses_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."batch_analyses_id_seq";
CREATE SEQUENCE "public"."batch_analyses_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for boss_jobs_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."boss_jobs_id_seq";
CREATE SEQUENCE "public"."boss_jobs_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for crawl_tasks_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."crawl_tasks_id_seq";
CREATE SEQUENCE "public"."crawl_tasks_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for job_descriptions_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."job_descriptions_id_seq";
CREATE SEQUENCE "public"."job_descriptions_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for match_analyses_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."match_analyses_id_seq";
CREATE SEQUENCE "public"."match_analyses_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for resume_chat_history_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."resume_chat_history_id_seq";
CREATE SEQUENCE "public"."resume_chat_history_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for resume_versions_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."resume_versions_id_seq";
CREATE SEQUENCE "public"."resume_versions_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for resumes_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."resumes_id_seq";
CREATE SEQUENCE "public"."resumes_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for system_logs_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."system_logs_id_seq";
CREATE SEQUENCE "public"."system_logs_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for user_statistics_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."user_statistics_id_seq";
CREATE SEQUENCE "public"."user_statistics_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for users_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."users_id_seq";
CREATE SEQUENCE "public"."users_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Table structure for batch_analyses
-- ----------------------------
DROP TABLE IF EXISTS "public"."batch_analyses";
CREATE TABLE "public"."batch_analyses" (
  "id" int4 NOT NULL DEFAULT nextval('batch_analyses_id_seq'::regclass),
  "batch_id" uuid NOT NULL DEFAULT uuid_generate_v4(),
  "resume_id" uuid NOT NULL,
  "crawl_task_id" uuid NOT NULL,
  "user_id" int4,
  "total_jobs" int4 DEFAULT 0,
  "analyzed_jobs" int4 DEFAULT 0,
  "avg_match_score" float4,
  "max_match_score" float4,
  "min_match_score" float4,
  "top_matched_jobs_json" jsonb,
  "common_missing_skills_json" jsonb,
  "common_suggestions_json" jsonb,
  "status" varchar(50) COLLATE "pg_catalog"."default" DEFAULT 'pending'::character varying,
  "progress" int4 DEFAULT 0,
  "started_at" timestamp(6),
  "completed_at" timestamp(6),
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP
)
;
COMMENT ON COLUMN "public"."batch_analyses"."avg_match_score" IS '平均匹配度
计算简历与每个职位的匹配度
取所有匹配度的平均值';
COMMENT ON COLUMN "public"."batch_analyses"."max_match_score" IS '最高匹配度

所有职位中匹配度最高的那个';
COMMENT ON COLUMN "public"."batch_analyses"."min_match_score" IS '最低匹配度

所有职位中匹配度最低的那个';
COMMENT ON COLUMN "public"."batch_analyses"."top_matched_jobs_json" IS '匹配度最高的职位列表

按匹配度排序后的 Top 10 个职位
包含职位信息、匹配度、匹配的技能、缺失的技能';

-- ----------------------------
-- Table structure for boss_jobs
-- ----------------------------
DROP TABLE IF EXISTS "public"."boss_jobs";
CREATE TABLE "public"."boss_jobs" (
  "id" int4 NOT NULL DEFAULT nextval('boss_jobs_id_seq'::regclass),
  "job_id" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "job_name" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "company_name" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "salary" varchar(100) COLLATE "pg_catalog"."default",
  "location" varchar(200) COLLATE "pg_catalog"."default",
  "experience" varchar(100) COLLATE "pg_catalog"."default",
  "education" varchar(100) COLLATE "pg_catalog"."default",
  "job_description" text COLLATE "pg_catalog"."default",
  "welfare_tags" jsonb,
  "crawled_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "task_id" uuid NOT NULL
)
;

-- ----------------------------
-- Table structure for crawl_tasks
-- ----------------------------
DROP TABLE IF EXISTS "public"."crawl_tasks";
CREATE TABLE "public"."crawl_tasks" (
  "id" int4 NOT NULL DEFAULT nextval('crawl_tasks_id_seq'::regclass),
  "task_id" uuid NOT NULL DEFAULT uuid_generate_v4(),
  "user_id" int4,
  "keyword" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "city" varchar(100) COLLATE "pg_catalog"."default",
  "max_pages" int4 DEFAULT 5,
  "status" varchar(50) COLLATE "pg_catalog"."default" DEFAULT 'pending'::character varying,
  "progress" int4 DEFAULT 0,
  "total_jobs" int4 DEFAULT 0,
  "crawled_jobs" int4 DEFAULT 0,
  "started_at" timestamp(6),
  "completed_at" timestamp(6),
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP
)
;

-- ----------------------------
-- Table structure for job_descriptions
-- ----------------------------
DROP TABLE IF EXISTS "public"."job_descriptions";
CREATE TABLE "public"."job_descriptions" (
  "id" int4 NOT NULL DEFAULT nextval('job_descriptions_id_seq'::regclass),
  "jd_id" uuid NOT NULL DEFAULT uuid_generate_v4(),
  "user_id" int4,
  "raw_text" text COLLATE "pg_catalog"."default" NOT NULL,
  "required_skills" jsonb,
  "preferred_skills" jsonb,
  "responsibilities" jsonb,
  "requirements" jsonb,
  "keywords" jsonb,
  "parsed" bool DEFAULT false,
  "parse_error" text COLLATE "pg_catalog"."default",
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP
)
;
COMMENT ON COLUMN "public"."job_descriptions"."raw_text" IS '用户输入的完整 JD 文本';
COMMENT ON COLUMN "public"."job_descriptions"."required_skills" IS 'AI 解析出的必需技能列表（JSONB）';
COMMENT ON COLUMN "public"."job_descriptions"."preferred_skills" IS 'AI 解析出的优先技能列表（JSONB）';
COMMENT ON COLUMN "public"."job_descriptions"."responsibilities" IS 'AI 解析出的工作职责列表（JSONB）';
COMMENT ON COLUMN "public"."job_descriptions"."requirements" IS 'AI 解析出的任职要求列表（JSONB）';
COMMENT ON COLUMN "public"."job_descriptions"."keywords" IS 'AI 提取的关键词列表（JSONB），用于搜索和匹配';
COMMENT ON COLUMN "public"."job_descriptions"."parsed" IS '是否已完成 AI 解析';
COMMENT ON COLUMN "public"."job_descriptions"."parse_error" IS '解析失败时的错误信息';
COMMENT ON TABLE "public"."job_descriptions" IS '职位描述表：存储用户输入的 JD 文本并解析出结构化信息用于简历匹配';

-- ----------------------------
-- Table structure for match_analyses
-- ----------------------------
DROP TABLE IF EXISTS "public"."match_analyses";
CREATE TABLE "public"."match_analyses" (
  "id" int4 NOT NULL DEFAULT nextval('match_analyses_id_seq'::regclass),
  "match_id" uuid NOT NULL DEFAULT uuid_generate_v4(),
  "resume_id" uuid NOT NULL,
  "jd_id" uuid NOT NULL,
  "user_id" int4,
  "overall_score" numeric(5,2),
  "skill_match_score" numeric(5,2),
  "experience_match_score" numeric(5,2),
  "education_match_score" numeric(5,2),
  "matched_skills" jsonb,
  "missing_skills" jsonb,
  "suggestions" jsonb,
  "analysis_report" text COLLATE "pg_catalog"."default",
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "strengths" jsonb DEFAULT '[]'::jsonb,
  "weaknesses" jsonb DEFAULT '[]'::jsonb
)
;
COMMENT ON COLUMN "public"."match_analyses"."overall_score" IS '总体匹配度评分 (0-100)';
COMMENT ON COLUMN "public"."match_analyses"."matched_skills" IS '简历中匹配的技能列表（JSONB）';
COMMENT ON COLUMN "public"."match_analyses"."missing_skills" IS '简历中缺失的技能列表（JSONB）';
COMMENT ON COLUMN "public"."match_analyses"."suggestions" IS 'AI 生成的优化建议列表（JSONB）';
COMMENT ON COLUMN "public"."match_analyses"."analysis_report" IS 'AI 生成的详细分析报告（Markdown 格式）';
COMMENT ON COLUMN "public"."match_analyses"."strengths" IS '候选人优势列表';
COMMENT ON COLUMN "public"."match_analyses"."weaknesses" IS '候选人劣势列表';
COMMENT ON TABLE "public"."match_analyses" IS '简历-JD 匹配分析表：存储简历与职位描述的匹配分析结果';

-- ----------------------------
-- Table structure for resume_chat_history
-- ----------------------------
DROP TABLE IF EXISTS "public"."resume_chat_history";
CREATE TABLE "public"."resume_chat_history" (
  "id" int4 NOT NULL DEFAULT nextval('resume_chat_history_id_seq'::regclass),
  "chat_id" uuid NOT NULL,
  "resume_id" uuid NOT NULL,
  "user_id" int4 NOT NULL,
  "role" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "content" text COLLATE "pg_catalog"."default" NOT NULL,
  "modified_section" text COLLATE "pg_catalog"."default",
  "section_type" varchar(50) COLLATE "pg_catalog"."default",
  "explanation" text COLLATE "pg_catalog"."default",
  "created_at" timestamptz(6) DEFAULT now()
)
;

-- ----------------------------
-- Table structure for resume_versions
-- ----------------------------
DROP TABLE IF EXISTS "public"."resume_versions";
CREATE TABLE "public"."resume_versions" (
  "id" int4 NOT NULL DEFAULT nextval('resume_versions_id_seq'::regclass),
  "version_id" uuid NOT NULL,
  "resume_id" uuid NOT NULL,
  "user_id" int4 NOT NULL,
  "content" text COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "created_at" timestamptz(6) DEFAULT now()
)
;

-- ----------------------------
-- Table structure for resumes
-- ----------------------------
DROP TABLE IF EXISTS "public"."resumes";
CREATE TABLE "public"."resumes" (
  "id" int4 NOT NULL DEFAULT nextval('resumes_id_seq'::regclass),
  "resume_id" uuid NOT NULL DEFAULT uuid_generate_v4(),
  "user_id" int4,
  "filename" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "file_size" int4 NOT NULL,
  "file_type" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "file_path" varchar(500) COLLATE "pg_catalog"."default",
  "name" varchar(100) COLLATE "pg_catalog"."default",
  "email" varchar(100) COLLATE "pg_catalog"."default",
  "phone" varchar(50) COLLATE "pg_catalog"."default",
  "target_position" varchar(100) COLLATE "pg_catalog"."default",
  "raw_text" text COLLATE "pg_catalog"."default",
  "markdown_text" text COLLATE "pg_catalog"."default",
  "education_json" jsonb,
  "skills_json" jsonb,
  "projects_json" jsonb,
  "work_experience_json" jsonb,
  "certifications_json" jsonb,
  "awards_json" jsonb,
  "parsed" bool DEFAULT false,
  "parse_error" text COLLATE "pg_catalog"."default",
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP
)
;

-- ----------------------------
-- Table structure for system_logs
-- ----------------------------
DROP TABLE IF EXISTS "public"."system_logs";
CREATE TABLE "public"."system_logs" (
  "id" int4 NOT NULL DEFAULT nextval('system_logs_id_seq'::regclass),
  "user_id" int4,
  "action" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "resource_type" varchar(50) COLLATE "pg_catalog"."default",
  "resource_id" uuid,
  "status" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "error_message" text COLLATE "pg_catalog"."default",
  "execution_time" float4,
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP
)
;

-- ----------------------------
-- Table structure for user_statistics
-- ----------------------------
DROP TABLE IF EXISTS "public"."user_statistics";
CREATE TABLE "public"."user_statistics" (
  "id" int4 NOT NULL DEFAULT nextval('user_statistics_id_seq'::regclass),
  "user_id" int4 NOT NULL,
  "total_resumes" int4 DEFAULT 0,
  "total_jds" int4 DEFAULT 0,
  "total_matches" int4 DEFAULT 0,
  "total_crawl_tasks" int4 DEFAULT 0,
  "last_login_at" timestamp(6),
  "last_activity_at" timestamp(6),
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP
)
;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS "public"."users";
CREATE TABLE "public"."users" (
  "id" int4 NOT NULL DEFAULT nextval('users_id_seq'::regclass),
  "username" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "email" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "password_hash" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "is_active" bool DEFAULT true
)
;

-- ----------------------------
-- Function structure for gin_extract_query_trgm
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."gin_extract_query_trgm"(text, internal, int2, internal, internal, internal, internal);
CREATE OR REPLACE FUNCTION "public"."gin_extract_query_trgm"(text, internal, int2, internal, internal, internal, internal)
  RETURNS "pg_catalog"."internal" AS '$libdir/pg_trgm', 'gin_extract_query_trgm'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for gin_extract_value_trgm
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."gin_extract_value_trgm"(text, internal);
CREATE OR REPLACE FUNCTION "public"."gin_extract_value_trgm"(text, internal)
  RETURNS "pg_catalog"."internal" AS '$libdir/pg_trgm', 'gin_extract_value_trgm'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for gin_trgm_consistent
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."gin_trgm_consistent"(internal, int2, text, int4, internal, internal, internal, internal);
CREATE OR REPLACE FUNCTION "public"."gin_trgm_consistent"(internal, int2, text, int4, internal, internal, internal, internal)
  RETURNS "pg_catalog"."bool" AS '$libdir/pg_trgm', 'gin_trgm_consistent'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for gin_trgm_triconsistent
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."gin_trgm_triconsistent"(internal, int2, text, int4, internal, internal, internal);
CREATE OR REPLACE FUNCTION "public"."gin_trgm_triconsistent"(internal, int2, text, int4, internal, internal, internal)
  RETURNS "pg_catalog"."char" AS '$libdir/pg_trgm', 'gin_trgm_triconsistent'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for gtrgm_compress
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."gtrgm_compress"(internal);
CREATE OR REPLACE FUNCTION "public"."gtrgm_compress"(internal)
  RETURNS "pg_catalog"."internal" AS '$libdir/pg_trgm', 'gtrgm_compress'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for gtrgm_consistent
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."gtrgm_consistent"(internal, text, int2, oid, internal);
CREATE OR REPLACE FUNCTION "public"."gtrgm_consistent"(internal, text, int2, oid, internal)
  RETURNS "pg_catalog"."bool" AS '$libdir/pg_trgm', 'gtrgm_consistent'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for gtrgm_decompress
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."gtrgm_decompress"(internal);
CREATE OR REPLACE FUNCTION "public"."gtrgm_decompress"(internal)
  RETURNS "pg_catalog"."internal" AS '$libdir/pg_trgm', 'gtrgm_decompress'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for gtrgm_distance
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."gtrgm_distance"(internal, text, int2, oid, internal);
CREATE OR REPLACE FUNCTION "public"."gtrgm_distance"(internal, text, int2, oid, internal)
  RETURNS "pg_catalog"."float8" AS '$libdir/pg_trgm', 'gtrgm_distance'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for gtrgm_in
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."gtrgm_in"(cstring);
CREATE OR REPLACE FUNCTION "public"."gtrgm_in"(cstring)
  RETURNS "public"."gtrgm" AS '$libdir/pg_trgm', 'gtrgm_in'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for gtrgm_options
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."gtrgm_options"(internal);
CREATE OR REPLACE FUNCTION "public"."gtrgm_options"(internal)
  RETURNS "pg_catalog"."void" AS '$libdir/pg_trgm', 'gtrgm_options'
  LANGUAGE c IMMUTABLE
  COST 1;

-- ----------------------------
-- Function structure for gtrgm_out
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."gtrgm_out"("public"."gtrgm");
CREATE OR REPLACE FUNCTION "public"."gtrgm_out"("public"."gtrgm")
  RETURNS "pg_catalog"."cstring" AS '$libdir/pg_trgm', 'gtrgm_out'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for gtrgm_penalty
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."gtrgm_penalty"(internal, internal, internal);
CREATE OR REPLACE FUNCTION "public"."gtrgm_penalty"(internal, internal, internal)
  RETURNS "pg_catalog"."internal" AS '$libdir/pg_trgm', 'gtrgm_penalty'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for gtrgm_picksplit
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."gtrgm_picksplit"(internal, internal);
CREATE OR REPLACE FUNCTION "public"."gtrgm_picksplit"(internal, internal)
  RETURNS "pg_catalog"."internal" AS '$libdir/pg_trgm', 'gtrgm_picksplit'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for gtrgm_same
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."gtrgm_same"("public"."gtrgm", "public"."gtrgm", internal);
CREATE OR REPLACE FUNCTION "public"."gtrgm_same"("public"."gtrgm", "public"."gtrgm", internal)
  RETURNS "pg_catalog"."internal" AS '$libdir/pg_trgm', 'gtrgm_same'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for gtrgm_union
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."gtrgm_union"(internal, internal);
CREATE OR REPLACE FUNCTION "public"."gtrgm_union"(internal, internal)
  RETURNS "public"."gtrgm" AS '$libdir/pg_trgm', 'gtrgm_union'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for set_limit
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."set_limit"(float4);
CREATE OR REPLACE FUNCTION "public"."set_limit"(float4)
  RETURNS "pg_catalog"."float4" AS '$libdir/pg_trgm', 'set_limit'
  LANGUAGE c VOLATILE STRICT
  COST 1;

-- ----------------------------
-- Function structure for show_limit
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."show_limit"();
CREATE OR REPLACE FUNCTION "public"."show_limit"()
  RETURNS "pg_catalog"."float4" AS '$libdir/pg_trgm', 'show_limit'
  LANGUAGE c STABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for show_trgm
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."show_trgm"(text);
CREATE OR REPLACE FUNCTION "public"."show_trgm"(text)
  RETURNS "pg_catalog"."_text" AS '$libdir/pg_trgm', 'show_trgm'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for similarity
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."similarity"(text, text);
CREATE OR REPLACE FUNCTION "public"."similarity"(text, text)
  RETURNS "pg_catalog"."float4" AS '$libdir/pg_trgm', 'similarity'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for similarity_dist
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."similarity_dist"(text, text);
CREATE OR REPLACE FUNCTION "public"."similarity_dist"(text, text)
  RETURNS "pg_catalog"."float4" AS '$libdir/pg_trgm', 'similarity_dist'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for similarity_op
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."similarity_op"(text, text);
CREATE OR REPLACE FUNCTION "public"."similarity_op"(text, text)
  RETURNS "pg_catalog"."bool" AS '$libdir/pg_trgm', 'similarity_op'
  LANGUAGE c STABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for strict_word_similarity
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."strict_word_similarity"(text, text);
CREATE OR REPLACE FUNCTION "public"."strict_word_similarity"(text, text)
  RETURNS "pg_catalog"."float4" AS '$libdir/pg_trgm', 'strict_word_similarity'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for strict_word_similarity_commutator_op
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."strict_word_similarity_commutator_op"(text, text);
CREATE OR REPLACE FUNCTION "public"."strict_word_similarity_commutator_op"(text, text)
  RETURNS "pg_catalog"."bool" AS '$libdir/pg_trgm', 'strict_word_similarity_commutator_op'
  LANGUAGE c STABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for strict_word_similarity_dist_commutator_op
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."strict_word_similarity_dist_commutator_op"(text, text);
CREATE OR REPLACE FUNCTION "public"."strict_word_similarity_dist_commutator_op"(text, text)
  RETURNS "pg_catalog"."float4" AS '$libdir/pg_trgm', 'strict_word_similarity_dist_commutator_op'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for strict_word_similarity_dist_op
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."strict_word_similarity_dist_op"(text, text);
CREATE OR REPLACE FUNCTION "public"."strict_word_similarity_dist_op"(text, text)
  RETURNS "pg_catalog"."float4" AS '$libdir/pg_trgm', 'strict_word_similarity_dist_op'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for strict_word_similarity_op
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."strict_word_similarity_op"(text, text);
CREATE OR REPLACE FUNCTION "public"."strict_word_similarity_op"(text, text)
  RETURNS "pg_catalog"."bool" AS '$libdir/pg_trgm', 'strict_word_similarity_op'
  LANGUAGE c STABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for update_updated_at_column
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."update_updated_at_column"();
CREATE OR REPLACE FUNCTION "public"."update_updated_at_column"()
  RETURNS "pg_catalog"."trigger" AS $BODY$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

-- ----------------------------
-- Function structure for uuid_generate_v1
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."uuid_generate_v1"();
CREATE OR REPLACE FUNCTION "public"."uuid_generate_v1"()
  RETURNS "pg_catalog"."uuid" AS '$libdir/uuid-ossp', 'uuid_generate_v1'
  LANGUAGE c VOLATILE STRICT
  COST 1;

-- ----------------------------
-- Function structure for uuid_generate_v1mc
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."uuid_generate_v1mc"();
CREATE OR REPLACE FUNCTION "public"."uuid_generate_v1mc"()
  RETURNS "pg_catalog"."uuid" AS '$libdir/uuid-ossp', 'uuid_generate_v1mc'
  LANGUAGE c VOLATILE STRICT
  COST 1;

-- ----------------------------
-- Function structure for uuid_generate_v3
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."uuid_generate_v3"("namespace" uuid, "name" text);
CREATE OR REPLACE FUNCTION "public"."uuid_generate_v3"("namespace" uuid, "name" text)
  RETURNS "pg_catalog"."uuid" AS '$libdir/uuid-ossp', 'uuid_generate_v3'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for uuid_generate_v4
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."uuid_generate_v4"();
CREATE OR REPLACE FUNCTION "public"."uuid_generate_v4"()
  RETURNS "pg_catalog"."uuid" AS '$libdir/uuid-ossp', 'uuid_generate_v4'
  LANGUAGE c VOLATILE STRICT
  COST 1;

-- ----------------------------
-- Function structure for uuid_generate_v5
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."uuid_generate_v5"("namespace" uuid, "name" text);
CREATE OR REPLACE FUNCTION "public"."uuid_generate_v5"("namespace" uuid, "name" text)
  RETURNS "pg_catalog"."uuid" AS '$libdir/uuid-ossp', 'uuid_generate_v5'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for uuid_nil
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."uuid_nil"();
CREATE OR REPLACE FUNCTION "public"."uuid_nil"()
  RETURNS "pg_catalog"."uuid" AS '$libdir/uuid-ossp', 'uuid_nil'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for uuid_ns_dns
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."uuid_ns_dns"();
CREATE OR REPLACE FUNCTION "public"."uuid_ns_dns"()
  RETURNS "pg_catalog"."uuid" AS '$libdir/uuid-ossp', 'uuid_ns_dns'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for uuid_ns_oid
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."uuid_ns_oid"();
CREATE OR REPLACE FUNCTION "public"."uuid_ns_oid"()
  RETURNS "pg_catalog"."uuid" AS '$libdir/uuid-ossp', 'uuid_ns_oid'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for uuid_ns_url
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."uuid_ns_url"();
CREATE OR REPLACE FUNCTION "public"."uuid_ns_url"()
  RETURNS "pg_catalog"."uuid" AS '$libdir/uuid-ossp', 'uuid_ns_url'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for uuid_ns_x500
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."uuid_ns_x500"();
CREATE OR REPLACE FUNCTION "public"."uuid_ns_x500"()
  RETURNS "pg_catalog"."uuid" AS '$libdir/uuid-ossp', 'uuid_ns_x500'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for word_similarity
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."word_similarity"(text, text);
CREATE OR REPLACE FUNCTION "public"."word_similarity"(text, text)
  RETURNS "pg_catalog"."float4" AS '$libdir/pg_trgm', 'word_similarity'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for word_similarity_commutator_op
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."word_similarity_commutator_op"(text, text);
CREATE OR REPLACE FUNCTION "public"."word_similarity_commutator_op"(text, text)
  RETURNS "pg_catalog"."bool" AS '$libdir/pg_trgm', 'word_similarity_commutator_op'
  LANGUAGE c STABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for word_similarity_dist_commutator_op
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."word_similarity_dist_commutator_op"(text, text);
CREATE OR REPLACE FUNCTION "public"."word_similarity_dist_commutator_op"(text, text)
  RETURNS "pg_catalog"."float4" AS '$libdir/pg_trgm', 'word_similarity_dist_commutator_op'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for word_similarity_dist_op
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."word_similarity_dist_op"(text, text);
CREATE OR REPLACE FUNCTION "public"."word_similarity_dist_op"(text, text)
  RETURNS "pg_catalog"."float4" AS '$libdir/pg_trgm', 'word_similarity_dist_op'
  LANGUAGE c IMMUTABLE STRICT
  COST 1;

-- ----------------------------
-- Function structure for word_similarity_op
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."word_similarity_op"(text, text);
CREATE OR REPLACE FUNCTION "public"."word_similarity_op"(text, text)
  RETURNS "pg_catalog"."bool" AS '$libdir/pg_trgm', 'word_similarity_op'
  LANGUAGE c STABLE STRICT
  COST 1;

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."batch_analyses_id_seq"
OWNED BY "public"."batch_analyses"."id";
SELECT setval('"public"."batch_analyses_id_seq"', 6, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."boss_jobs_id_seq"
OWNED BY "public"."boss_jobs"."id";
SELECT setval('"public"."boss_jobs_id_seq"', 376, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."crawl_tasks_id_seq"
OWNED BY "public"."crawl_tasks"."id";
SELECT setval('"public"."crawl_tasks_id_seq"', 37, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."job_descriptions_id_seq"
OWNED BY "public"."job_descriptions"."id";
SELECT setval('"public"."job_descriptions_id_seq"', 3, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."match_analyses_id_seq"
OWNED BY "public"."match_analyses"."id";
SELECT setval('"public"."match_analyses_id_seq"', 4, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."resume_chat_history_id_seq"
OWNED BY "public"."resume_chat_history"."id";
SELECT setval('"public"."resume_chat_history_id_seq"', 6, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."resume_versions_id_seq"
OWNED BY "public"."resume_versions"."id";
SELECT setval('"public"."resume_versions_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."resumes_id_seq"
OWNED BY "public"."resumes"."id";
SELECT setval('"public"."resumes_id_seq"', 4, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."system_logs_id_seq"
OWNED BY "public"."system_logs"."id";
SELECT setval('"public"."system_logs_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."user_statistics_id_seq"
OWNED BY "public"."user_statistics"."id";
SELECT setval('"public"."user_statistics_id_seq"', 5, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."users_id_seq"
OWNED BY "public"."users"."id";
SELECT setval('"public"."users_id_seq"', 5, true);

-- ----------------------------
-- Indexes structure for table batch_analyses
-- ----------------------------
CREATE INDEX "idx_batch_analyses_batch_id" ON "public"."batch_analyses" USING btree (
  "batch_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "idx_batch_analyses_created_at" ON "public"."batch_analyses" USING btree (
  "created_at" "pg_catalog"."timestamp_ops" ASC NULLS LAST
);
CREATE INDEX "idx_batch_analyses_resume_id" ON "public"."batch_analyses" USING btree (
  "resume_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "idx_batch_analyses_user_id" ON "public"."batch_analyses" USING btree (
  "user_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table batch_analyses
-- ----------------------------
ALTER TABLE "public"."batch_analyses" ADD CONSTRAINT "batch_analyses_batch_id_key" UNIQUE ("batch_id");

-- ----------------------------
-- Checks structure for table batch_analyses
-- ----------------------------
ALTER TABLE "public"."batch_analyses" ADD CONSTRAINT "batch_analyses_progress_check" CHECK (progress >= 0 AND progress <= 100);
ALTER TABLE "public"."batch_analyses" ADD CONSTRAINT "batch_analyses_status_check" CHECK (status::text = ANY (ARRAY['pending'::character varying, 'running'::character varying, 'completed'::character varying, 'failed'::character varying]::text[]));

-- ----------------------------
-- Primary Key structure for table batch_analyses
-- ----------------------------
ALTER TABLE "public"."batch_analyses" ADD CONSTRAINT "batch_analyses_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table boss_jobs
-- ----------------------------
CREATE INDEX "idx_boss_jobs_company" ON "public"."boss_jobs" USING btree (
  "company_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_boss_jobs_crawled_at" ON "public"."boss_jobs" USING btree (
  "crawled_at" "pg_catalog"."timestamp_ops" ASC NULLS LAST
);
CREATE INDEX "idx_boss_jobs_job_id" ON "public"."boss_jobs" USING btree (
  "job_id" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_boss_jobs_position" ON "public"."boss_jobs" USING btree (
  "job_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_boss_jobs_search" ON "public"."boss_jobs" USING gin (
  ((company_name::text || ' '::text) || job_name::text) COLLATE "pg_catalog"."default" "public"."gin_trgm_ops"
);
CREATE INDEX "ix_boss_jobs_task_id" ON "public"."boss_jobs" USING btree (
  "task_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table boss_jobs
-- ----------------------------
ALTER TABLE "public"."boss_jobs" ADD CONSTRAINT "boss_jobs_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table crawl_tasks
-- ----------------------------
CREATE INDEX "idx_crawl_tasks_created_at" ON "public"."crawl_tasks" USING btree (
  "created_at" "pg_catalog"."timestamp_ops" ASC NULLS LAST
);
CREATE INDEX "idx_crawl_tasks_status" ON "public"."crawl_tasks" USING btree (
  "status" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_crawl_tasks_task_id" ON "public"."crawl_tasks" USING btree (
  "task_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "idx_crawl_tasks_user_id" ON "public"."crawl_tasks" USING btree (
  "user_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table crawl_tasks
-- ----------------------------
ALTER TABLE "public"."crawl_tasks" ADD CONSTRAINT "crawl_tasks_task_id_key" UNIQUE ("task_id");

-- ----------------------------
-- Checks structure for table crawl_tasks
-- ----------------------------
ALTER TABLE "public"."crawl_tasks" ADD CONSTRAINT "crawl_tasks_status_check" CHECK (status::text = ANY (ARRAY['pending'::character varying, 'running'::character varying, 'completed'::character varying, 'failed'::character varying]::text[]));
ALTER TABLE "public"."crawl_tasks" ADD CONSTRAINT "crawl_tasks_progress_check" CHECK (progress >= 0 AND progress <= 100);

-- ----------------------------
-- Primary Key structure for table crawl_tasks
-- ----------------------------
ALTER TABLE "public"."crawl_tasks" ADD CONSTRAINT "crawl_tasks_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table job_descriptions
-- ----------------------------
CREATE INDEX "idx_jd_created_at" ON "public"."job_descriptions" USING btree (
  "created_at" "pg_catalog"."timestamp_ops" ASC NULLS LAST
);
CREATE INDEX "idx_jd_jd_id" ON "public"."job_descriptions" USING btree (
  "jd_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "idx_jd_keywords" ON "public"."job_descriptions" USING gin (
  "keywords" "pg_catalog"."jsonb_ops"
);
CREATE INDEX "idx_jd_parsed" ON "public"."job_descriptions" USING btree (
  "parsed" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "idx_jd_required_skills" ON "public"."job_descriptions" USING gin (
  "required_skills" "pg_catalog"."jsonb_ops"
);
CREATE INDEX "idx_jd_user_id" ON "public"."job_descriptions" USING btree (
  "user_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table job_descriptions
-- ----------------------------
ALTER TABLE "public"."job_descriptions" ADD CONSTRAINT "job_descriptions_jd_id_key" UNIQUE ("jd_id");

-- ----------------------------
-- Primary Key structure for table job_descriptions
-- ----------------------------
ALTER TABLE "public"."job_descriptions" ADD CONSTRAINT "job_descriptions_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table match_analyses
-- ----------------------------
CREATE INDEX "idx_match_created_at" ON "public"."match_analyses" USING btree (
  "created_at" "pg_catalog"."timestamp_ops" ASC NULLS LAST
);
CREATE INDEX "idx_match_jd_id" ON "public"."match_analyses" USING btree (
  "jd_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "idx_match_match_id" ON "public"."match_analyses" USING btree (
  "match_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "idx_match_overall_score" ON "public"."match_analyses" USING btree (
  "overall_score" "pg_catalog"."numeric_ops" ASC NULLS LAST
);
CREATE INDEX "idx_match_resume_id" ON "public"."match_analyses" USING btree (
  "resume_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "idx_match_user_id" ON "public"."match_analyses" USING btree (
  "user_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table match_analyses
-- ----------------------------
ALTER TABLE "public"."match_analyses" ADD CONSTRAINT "match_analyses_match_id_key" UNIQUE ("match_id");

-- ----------------------------
-- Primary Key structure for table match_analyses
-- ----------------------------
ALTER TABLE "public"."match_analyses" ADD CONSTRAINT "match_analyses_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table resume_chat_history
-- ----------------------------
CREATE UNIQUE INDEX "ix_resume_chat_history_chat_id" ON "public"."resume_chat_history" USING btree (
  "chat_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "ix_resume_chat_history_created_at" ON "public"."resume_chat_history" USING btree (
  "created_at" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);
CREATE INDEX "ix_resume_chat_history_id" ON "public"."resume_chat_history" USING btree (
  "id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_resume_chat_history_resume_id" ON "public"."resume_chat_history" USING btree (
  "resume_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "ix_resume_chat_history_user_id" ON "public"."resume_chat_history" USING btree (
  "user_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Checks structure for table resume_chat_history
-- ----------------------------
ALTER TABLE "public"."resume_chat_history" ADD CONSTRAINT "check_chat_role" CHECK (role::text = ANY (ARRAY['user'::character varying, 'assistant'::character varying]::text[]));

-- ----------------------------
-- Primary Key structure for table resume_chat_history
-- ----------------------------
ALTER TABLE "public"."resume_chat_history" ADD CONSTRAINT "resume_chat_history_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table resume_versions
-- ----------------------------
CREATE INDEX "ix_resume_versions_created_at" ON "public"."resume_versions" USING btree (
  "created_at" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);
CREATE INDEX "ix_resume_versions_id" ON "public"."resume_versions" USING btree (
  "id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "ix_resume_versions_resume_id" ON "public"."resume_versions" USING btree (
  "resume_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "ix_resume_versions_user_id" ON "public"."resume_versions" USING btree (
  "user_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE UNIQUE INDEX "ix_resume_versions_version_id" ON "public"."resume_versions" USING btree (
  "version_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table resume_versions
-- ----------------------------
ALTER TABLE "public"."resume_versions" ADD CONSTRAINT "resume_versions_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table resumes
-- ----------------------------
CREATE INDEX "idx_resumes_created_at" ON "public"."resumes" USING btree (
  "created_at" "pg_catalog"."timestamp_ops" ASC NULLS LAST
);
CREATE INDEX "idx_resumes_name" ON "public"."resumes" USING gin (
  "name" COLLATE "pg_catalog"."default" "public"."gin_trgm_ops"
);
CREATE INDEX "idx_resumes_resume_id" ON "public"."resumes" USING btree (
  "resume_id" "pg_catalog"."uuid_ops" ASC NULLS LAST
);
CREATE INDEX "idx_resumes_user_id" ON "public"."resumes" USING btree (
  "user_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table resumes
-- ----------------------------
CREATE TRIGGER "update_resumes_updated_at" BEFORE UPDATE ON "public"."resumes"
FOR EACH ROW
EXECUTE PROCEDURE "public"."update_updated_at_column"();

-- ----------------------------
-- Uniques structure for table resumes
-- ----------------------------
ALTER TABLE "public"."resumes" ADD CONSTRAINT "resumes_resume_id_key" UNIQUE ("resume_id");

-- ----------------------------
-- Primary Key structure for table resumes
-- ----------------------------
ALTER TABLE "public"."resumes" ADD CONSTRAINT "resumes_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table system_logs
-- ----------------------------
CREATE INDEX "idx_logs_action" ON "public"."system_logs" USING btree (
  "action" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_logs_created_at" ON "public"."system_logs" USING btree (
  "created_at" "pg_catalog"."timestamp_ops" ASC NULLS LAST
);
CREATE INDEX "idx_logs_status" ON "public"."system_logs" USING btree (
  "status" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_logs_user_id" ON "public"."system_logs" USING btree (
  "user_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Checks structure for table system_logs
-- ----------------------------
ALTER TABLE "public"."system_logs" ADD CONSTRAINT "system_logs_status_check" CHECK (status::text = ANY (ARRAY['success'::character varying, 'error'::character varying]::text[]));

-- ----------------------------
-- Primary Key structure for table system_logs
-- ----------------------------
ALTER TABLE "public"."system_logs" ADD CONSTRAINT "system_logs_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table user_statistics
-- ----------------------------
CREATE INDEX "idx_stats_user_id" ON "public"."user_statistics" USING btree (
  "user_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table user_statistics
-- ----------------------------
CREATE TRIGGER "update_stats_updated_at" BEFORE UPDATE ON "public"."user_statistics"
FOR EACH ROW
EXECUTE PROCEDURE "public"."update_updated_at_column"();

-- ----------------------------
-- Uniques structure for table user_statistics
-- ----------------------------
ALTER TABLE "public"."user_statistics" ADD CONSTRAINT "user_statistics_user_id_key" UNIQUE ("user_id");

-- ----------------------------
-- Primary Key structure for table user_statistics
-- ----------------------------
ALTER TABLE "public"."user_statistics" ADD CONSTRAINT "user_statistics_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table users
-- ----------------------------
CREATE INDEX "idx_users_email" ON "public"."users" USING btree (
  "email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_users_username" ON "public"."users" USING btree (
  "username" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table users
-- ----------------------------
CREATE TRIGGER "update_users_updated_at" BEFORE UPDATE ON "public"."users"
FOR EACH ROW
EXECUTE PROCEDURE "public"."update_updated_at_column"();

-- ----------------------------
-- Uniques structure for table users
-- ----------------------------
ALTER TABLE "public"."users" ADD CONSTRAINT "users_username_key" UNIQUE ("username");
ALTER TABLE "public"."users" ADD CONSTRAINT "users_email_key" UNIQUE ("email");

-- ----------------------------
-- Primary Key structure for table users
-- ----------------------------
ALTER TABLE "public"."users" ADD CONSTRAINT "users_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Foreign Keys structure for table batch_analyses
-- ----------------------------
ALTER TABLE "public"."batch_analyses" ADD CONSTRAINT "batch_analyses_crawl_task_id_fkey" FOREIGN KEY ("crawl_task_id") REFERENCES "public"."crawl_tasks" ("task_id") ON DELETE CASCADE ON UPDATE NO ACTION;
ALTER TABLE "public"."batch_analyses" ADD CONSTRAINT "batch_analyses_resume_id_fkey" FOREIGN KEY ("resume_id") REFERENCES "public"."resumes" ("resume_id") ON DELETE CASCADE ON UPDATE NO ACTION;
ALTER TABLE "public"."batch_analyses" ADD CONSTRAINT "batch_analyses_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table boss_jobs
-- ----------------------------
ALTER TABLE "public"."boss_jobs" ADD CONSTRAINT "boss_jobs_task_id_fkey" FOREIGN KEY ("task_id") REFERENCES "public"."crawl_tasks" ("task_id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table crawl_tasks
-- ----------------------------
ALTER TABLE "public"."crawl_tasks" ADD CONSTRAINT "crawl_tasks_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table job_descriptions
-- ----------------------------
ALTER TABLE "public"."job_descriptions" ADD CONSTRAINT "job_descriptions_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table match_analyses
-- ----------------------------
ALTER TABLE "public"."match_analyses" ADD CONSTRAINT "match_analyses_jd_id_fkey" FOREIGN KEY ("jd_id") REFERENCES "public"."job_descriptions" ("jd_id") ON DELETE CASCADE ON UPDATE NO ACTION;
ALTER TABLE "public"."match_analyses" ADD CONSTRAINT "match_analyses_resume_id_fkey" FOREIGN KEY ("resume_id") REFERENCES "public"."resumes" ("resume_id") ON DELETE CASCADE ON UPDATE NO ACTION;
ALTER TABLE "public"."match_analyses" ADD CONSTRAINT "match_analyses_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table resume_chat_history
-- ----------------------------
ALTER TABLE "public"."resume_chat_history" ADD CONSTRAINT "resume_chat_history_resume_id_fkey" FOREIGN KEY ("resume_id") REFERENCES "public"."resumes" ("resume_id") ON DELETE CASCADE ON UPDATE NO ACTION;
ALTER TABLE "public"."resume_chat_history" ADD CONSTRAINT "resume_chat_history_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table resume_versions
-- ----------------------------
ALTER TABLE "public"."resume_versions" ADD CONSTRAINT "resume_versions_resume_id_fkey" FOREIGN KEY ("resume_id") REFERENCES "public"."resumes" ("resume_id") ON DELETE CASCADE ON UPDATE NO ACTION;
ALTER TABLE "public"."resume_versions" ADD CONSTRAINT "resume_versions_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table resumes
-- ----------------------------
ALTER TABLE "public"."resumes" ADD CONSTRAINT "resumes_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table system_logs
-- ----------------------------
ALTER TABLE "public"."system_logs" ADD CONSTRAINT "system_logs_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users" ("id") ON DELETE SET NULL ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table user_statistics
-- ----------------------------
ALTER TABLE "public"."user_statistics" ADD CONSTRAINT "user_statistics_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

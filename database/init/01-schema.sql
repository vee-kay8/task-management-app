-- ===================================
-- DATABASE INITIALIZATION SCRIPT
-- ===================================
-- Purpose: Creates database schema for Task Management Application
-- This script runs automatically when PostgreSQL container starts for the first time

-- Enable UUID extension for generating unique identifiers
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ===================================
-- ENUMS (Custom Types)
-- ===================================

-- User roles define permission levels
-- ADMIN: Full access to all resources
-- MANAGER: Can manage projects and assign tasks
-- MEMBER: Can create and manage own tasks
-- VIEWER: Read-only access
CREATE TYPE user_role AS ENUM ('ADMIN', 'MANAGER', 'MEMBER', 'VIEWER');

-- Task status represents current state in workflow
CREATE TYPE task_status AS ENUM ('TODO', 'IN_PROGRESS', 'IN_REVIEW', 'DONE', 'ARCHIVED');

-- Task priority for importance ranking
CREATE TYPE task_priority AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'URGENT');

-- Project status
CREATE TYPE project_status AS ENUM ('PLANNING', 'ACTIVE', 'ON_HOLD', 'COMPLETED', 'ARCHIVED');

-- ===================================
-- TABLE: users
-- ===================================
-- Stores user account information
CREATE TABLE users (
    -- Primary key: UUID for global uniqueness
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Authentication fields
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- bcrypt hashed password
    
    -- User profile
    full_name VARCHAR(255) NOT NULL,
    avatar_url VARCHAR(500),  -- Profile picture URL (S3)
    
    -- Authorization
    role user_role DEFAULT 'MEMBER' NOT NULL,
    
    -- Account status
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    
    -- Timestamps for audit trail
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Indexes for faster queries
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(is_active);

-- ===================================
-- TABLE: projects
-- ===================================
-- Organizes tasks into projects/workspaces
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Project details
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status project_status DEFAULT 'PLANNING' NOT NULL,
    
    -- Color coding for UI (hex color)
    color VARCHAR(7) DEFAULT '#3B82F6',
    
    -- Ownership
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Dates
    start_date DATE,
    end_date DATE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_projects_owner ON projects(owner_id);
CREATE INDEX idx_projects_status ON projects(status);

-- ===================================
-- TABLE: project_members
-- ===================================
-- Many-to-many relationship: Users can be members of multiple projects
CREATE TABLE project_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- References
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Member-specific role in this project
    role user_role DEFAULT 'MEMBER' NOT NULL,
    
    -- Timestamps
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Prevent duplicate memberships
    UNIQUE(project_id, user_id)
);

CREATE INDEX idx_project_members_project ON project_members(project_id);
CREATE INDEX idx_project_members_user ON project_members(user_id);

-- ===================================
-- TABLE: tasks
-- ===================================
-- Core table for task management
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Task content
    title VARCHAR(500) NOT NULL,
    description TEXT,
    
    -- Status and priority
    status task_status DEFAULT 'TODO' NOT NULL,
    priority task_priority DEFAULT 'MEDIUM' NOT NULL,
    
    -- Organization
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    
    -- Assignment
    assignee_id UUID REFERENCES users(id) ON DELETE SET NULL,
    reporter_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Position for drag-and-drop ordering within status column
    position INTEGER DEFAULT 0,
    
    -- Dates
    due_date TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Estimate in hours (for time tracking)
    estimated_hours DECIMAL(5,2),
    actual_hours DECIMAL(5,2),
    
    -- Tags for categorization (stored as JSON array)
    tags JSONB DEFAULT '[]',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_assignee ON tasks(assignee_id);
CREATE INDEX idx_tasks_reporter ON tasks(reporter_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_position ON tasks(project_id, status, position);
CREATE INDEX idx_tasks_tags ON tasks USING GIN(tags);  -- GIN index for JSONB

-- ===================================
-- TABLE: comments
-- ===================================
-- Discussion thread for each task
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- References
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Comment content (supports markdown)
    content TEXT NOT NULL,
    
    -- Threading support (optional)
    parent_comment_id UUID REFERENCES comments(id) ON DELETE CASCADE,
    
    -- Edit tracking
    is_edited BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_comments_task ON comments(task_id);
CREATE INDEX idx_comments_user ON comments(user_id);
CREATE INDEX idx_comments_parent ON comments(parent_comment_id);

-- ===================================
-- TABLE: attachments
-- ===================================
-- File attachments for tasks
CREATE TABLE attachments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- References
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    uploaded_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- File information
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,  -- Size in bytes
    mime_type VARCHAR(100) NOT NULL,
    
    -- Storage location (S3 URL or path)
    storage_url VARCHAR(1000) NOT NULL,
    storage_key VARCHAR(500) NOT NULL,  -- S3 key for deletion
    
    -- Timestamps
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_attachments_task ON attachments(task_id);
CREATE INDEX idx_attachments_user ON attachments(uploaded_by);

-- ===================================
-- TABLE: activity_log
-- ===================================
-- Audit trail for all changes
CREATE TABLE activity_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- References
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    
    -- Activity details
    action VARCHAR(100) NOT NULL,  -- e.g., 'created_task', 'updated_status', 'added_comment'
    entity_type VARCHAR(50) NOT NULL,  -- 'task', 'project', 'comment', etc.
    
    -- Changes made (JSON object storing before/after values)
    changes JSONB,
    
    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_activity_log_user ON activity_log(user_id);
CREATE INDEX idx_activity_log_project ON activity_log(project_id);
CREATE INDEX idx_activity_log_task ON activity_log(task_id);
CREATE INDEX idx_activity_log_created ON activity_log(created_at);

-- ===================================
-- FUNCTIONS AND TRIGGERS
-- ===================================

-- Function to automatically update 'updated_at' timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update trigger to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_comments_updated_at BEFORE UPDATE ON comments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ===================================
-- SEED DATA (Development Only)
-- ===================================

-- Insert demo admin user
-- Password: 'admin123' (will be properly hashed in application)
INSERT INTO users (email, password_hash, full_name, role, email_verified) VALUES
    ('admin@taskapp.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyG3xoZB3pJu', 'Admin User', 'ADMIN', TRUE),
    ('john@taskapp.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyG3xoZB3pJu', 'John Doe', 'MANAGER', TRUE),
    ('jane@taskapp.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyG3xoZB3pJu', 'Jane Smith', 'MEMBER', TRUE);

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Database schema created successfully!';
    RAISE NOTICE 'Demo users created:';
    RAISE NOTICE '  - admin@taskapp.com (password: admin123)';
    RAISE NOTICE '  - john@taskapp.com (password: admin123)';
    RAISE NOTICE '  - jane@taskapp.com (password: admin123)';
END $$;

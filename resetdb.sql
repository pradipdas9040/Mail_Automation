-- supabase db: https://supabase.com/dashboard/project/oxsebytemqzoumgsrwgo/sql/8a5f9d10-ebd2-435c-9b13-2617a8ad4256

-- Drop and recreate the table with 'dob' column
DROP TABLE IF EXISTS public.user_entries;

-- Create the user_entries table with all fields from your Streamlit app
CREATE TABLE IF NOT EXISTS public.user_entries (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    dob DATE,
    dob_key VARCHAR(10) NOT NULL,
    email VARCHAR(255) NOT NULL,
    emoji VARCHAR(10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_user_entries_dob_key ON public.user_entries(dob_key);
CREATE INDEX IF NOT EXISTS idx_user_entries_email ON public.user_entries(email);
CREATE INDEX IF NOT EXISTS idx_user_entries_created_at ON public.user_entries(created_at DESC);

-- Enable Row Level Security
ALTER TABLE public.user_entries ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (for development)
-- IMPORTANT: For production, you'd want more restrictive policies
CREATE POLICY "Enable all operations for all users" 
    ON public.user_entries 
    FOR ALL 
    USING (true)
    WITH CHECK (true);

-- Optional: Add a trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_entries_updated_at
    BEFORE UPDATE ON public.user_entries
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant necessary permissions
GRANT ALL ON public.user_entries TO anon, authenticated;
GRANT USAGE ON SEQUENCE user_entries_id_seq TO anon, authenticated;

select * from public.user_entries;

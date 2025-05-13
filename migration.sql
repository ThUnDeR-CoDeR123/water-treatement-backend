-- First drop the foreign key constraints
ALTER TABLE plantflowparameter DROP CONSTRAINT IF EXISTS plantflowparameter_flow_parameter_id_fkey;
ALTER TABLE plantchemical DROP CONSTRAINT IF EXISTS plantchemical_chemical_id_fkey;
ALTER TABLE plantequipment DROP CONSTRAINT IF EXISTS plantequipment_equipment_id_fkey;

-- Drop association tables that reference these tables
DROP TABLE IF EXISTS planttypetoflowparameter;
DROP TABLE IF EXISTS planttypetochemical;
DROP TABLE IF EXISTS planttypetoequipment;

-- Drop the main tables
DROP TABLE IF EXISTS flowparameter;
DROP TABLE IF EXISTS chemical;
DROP TABLE IF EXISTS equipment;

-- Add new columns to plantequipment
ALTER TABLE plantequipment ADD COLUMN equipment_name VARCHAR NOT NULL;
ALTER TABLE plantequipment ADD COLUMN equipment_type VARCHAR;

-- Add new columns to plantchemical
ALTER TABLE plantchemical ADD COLUMN chemical_name VARCHAR NOT NULL;
ALTER TABLE plantchemical ADD COLUMN chemical_unit VARCHAR;

-- Add new columns to plantflowparameter
ALTER TABLE plantflowparameter ADD COLUMN parameter_name VARCHAR NOT NULL;
ALTER TABLE plantflowparameter ADD COLUMN parameter_unit VARCHAR;

""" Contains functions for converting between metric and imperial units.
	Separate functions for converting between systems."""
import math

def in_to_mm(inches):
	""" Converts inches to millimeters. Returns mm."""
	
	mm = inches * 25.4
	return mm
	
def mm_to_in(mm):
	""" Converts millimeters to inches. Returns inches."""
	
	inches = mm / 25.4
	return inches
	
def lb_to_kg(lb):
	""" Converts pounds to kilograms. Returns kg."""
	
	kg = lb / 2.2
	return kg

def kg_to_lb(kg):
	""" Converts kilograms to pounds. Returns lb."""
	
	lb = kg * 2.2
	return lb
	
def rad_to_deg(rad):
	""" Converts radians to degrees."""
	deg = rad * 180/math.pi
	
	return deg	

def deg_to_rad(deg):
	""" Converts degrees to radians."""
	rad = deg / 180 * math.pi
	
	return rad	
	
# ~~ End ~~

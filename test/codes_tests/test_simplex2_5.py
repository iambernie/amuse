import os.path
import numpy
from amuse.test.amusetest import TestWithMPI

from amuse.community.simplex2_5.interface import SimpleXInterface, SimpleX
from amuse.units import units
from amuse.datamodel import Particles
default_options = dict(number_of_workers=2, redirection="none")
default_options = dict(number_of_workers=1)#,debugger='gdb')

class TestSimpleXInterface(TestWithMPI):

    def test1(self):
        print "Test 1: initialization"
        instance = SimpleXInterface(**default_options)
        self.assertEqual(0, instance.set_output_directory(instance.output_directory))
        self.assertEqual(0, instance.initialize_code())
        self.assertEqual(0, instance.commit_parameters())
        self.assertEqual(0, instance.cleanup_code())
        instance.stop()
    
    def test2(self):
        print "Test 2: commit_particles, getters and setters"
        instance = SimpleXInterface(**default_options)
        self.assertEqual(0, instance.set_output_directory(instance.output_directory))
        self.assertEqual(0, instance.initialize_code())
        self.assertEqual(0, instance.commit_parameters())
        
        input_file = os.path.join(instance.data_directory, 'vertices_test3.txt')
        x, y, z, n_H, flux, X_ion,u = read_input_file(input_file)
        x=numpy.array(x)
        y=numpy.array(y)
        z=numpy.array(z)
        number_of_particles = len(x)
        indices, errors = instance.new_particle(x, y, z, n_H, flux, X_ion,u)
        self.assertEqual(errors, [0]*number_of_particles)
        self.assertEqual(indices, range(number_of_particles))
        self.assertEqual(0, instance.commit_particles())
        x_out, y_out, z_out, n_H_out, flux_out, X_ion_out,u_out, error = instance.get_state(indices)

        self.assertAlmostEqual((x-x_out)/13200., numpy.zeros_like(x), 7)
        self.assertAlmostEqual((y-y_out)/13200., numpy.zeros_like(x), 7)
        self.assertAlmostEqual((z-z_out)/13200., numpy.zeros_like(x), 7)
        self.assertAlmostEqual(flux,flux_out, 7)
        self.assertAlmostEqual(n_H,n_H_out, 7)
        self.assertAlmostEqual(X_ion,X_ion_out, 7)
        self.assertAlmostRelativeEqual(u,u_out, 7)
        
        
        
        x, y, z, n_H, flux, X_ion,u, error = instance.get_state(0)
        for expected, received in zip([0, 0, 0, 0.001, 5.0, 0.0, 831447247704,0], 
                [x, y, z, n_H, flux, X_ion, u,error]):
            self.assertAlmostRelativeEqual(expected, received,6)
        x, y, z, error1 = instance.get_position(0)
        n_H, error2     = instance.get_density(0)
        flux, error3    = instance.get_flux(0)
        X_ion, error4   = instance.get_ionisation(0)
        for expected, received in zip([0.,0.,0., 0.001, 5.0, 0.0, 0, 0, 0, 0], 
                [x, y, z, n_H, flux, X_ion, error1, error2, error3, error4]):
            self.assertAlmostRelativeEqual(expected, received, 5)
        
        self.assertEqual(0, instance.set_state(3, 1.0, 2.0, 3.0, 4.0, 5.0, 0.6,77.0))
        x, y, z, n_H, flux, X_ion, u,error = instance.get_state(3)
        for expected, received in zip([1.0, 2.0, 3.0, 4.0, 5.0, 0.6, 77,0], 
                [x, y, z, n_H, flux, X_ion,u, error]):
            self.assertAlmostRelativeEqual(expected, received, 5)
        self.assertEqual(0, instance.set_position(4, 3.0, 2.0, 1.0))
        self.assertEqual(0, instance.set_density(4, 0.6))
        self.assertEqual(0, instance.set_flux(4, 0.5))
        self.assertEqual(0, instance.set_ionisation(4, 0.4))
        self.assertEqual(0, instance.set_internal_energy(4, 1234.))
        x, y, z, n_H, flux, X_ion,u, error = instance.get_state(4)
        for expected, received in zip([3.0, 2.0, 1.0, 0.6, 0.5, 0.4,1234., 0], 
                [x, y, z, n_H, flux, X_ion,u, error]):
            self.assertAlmostRelativeEqual(expected, received, 5)


        self.assertEqual(0, instance.set_dinternal_energy_dt(4, 12345.))
        du_dt,err=instance.get_dinternal_energy_dt(4)
        self.assertEqual(12345, du_dt)
        
        self.assertEqual(0, instance.cleanup_code())
        instance.stop()
    
    def test3(self):
        print "Test 3: evolve"
        instance = SimpleXInterface(**default_options)
        self.assertEqual(0, instance.set_output_directory(instance.output_directory))
        self.assertEqual(0, instance.initialize_code())
        self.assertEqual(0, instance.commit_parameters())
        
        input_file = os.path.join(instance.data_directory, 'vertices_test3.txt')
        x, y, z, n_H, flux, X_ion,u = read_input_file(input_file)

        number_of_particles = len(x)
        indices, errors = instance.new_particle(x, y, z, n_H, flux, X_ion,u)
        self.assertEqual(errors, [0]*number_of_particles)
        self.assertEqual(indices, range(number_of_particles))
        
        self.assertEqual(0, instance.commit_particles())
        
        X_ion, errors = instance.get_ionisation(indices)
        self.assertEqual(errors, [0]*number_of_particles)
        self.assertAlmostEqual(X_ion.sum()/number_of_particles, 0.0)
        
        density, errors = instance.get_density(indices)
        self.assertEqual(errors, [0]*number_of_particles)
        self.assertAlmostEqual(density.sum(), 1.0,6)
        
        self.assertEqual(0, instance.evolve_model(0.5))

        density, errors = instance.get_density(indices)
        self.assertEqual(errors, [0]*number_of_particles)
        self.assertAlmostEqual(density.sum(), 1.0,6)
        
        flux, errors = instance.get_flux(indices)
        self.assertEqual(errors, [0]*number_of_particles)
        self.assertEqual(flux.sum(), 5.0)
        
        X_ion, errors = instance.get_ionisation(indices)
        self.assertEqual(errors, [0]*number_of_particles)
        self.assertAlmostEqual(X_ion.sum()/number_of_particles, 0.000930585139546)
        
        self.assertEqual(0, instance.cleanup_code())
        instance.stop()

    def test4(self):
        print "Test 4: set boxsize, hilbert_order, timestep"
        instance = SimpleXInterface(**default_options)
        self.assertEqual(0, instance.set_output_directory(instance.output_directory))
        self.assertEqual(0, instance.initialize_code())
        
        instance.set_box_size(16384.)
        instance.set_hilbert_order(1)
        instance.set_timestep(0.5)
                
        self.assertEqual(0, instance.commit_parameters())
        
        self.assertEqual(16384.,instance.get_box_size()['box_size'])
        self.assertEqual(1,instance.get_hilbert_order()['hilbert_order'])
        self.assertEqual(0.5,instance.get_timestep()['timestep'])

        input_file = os.path.join(instance.data_directory, 'vertices_test3.txt')
        x, y, z, n_H, flux, X_ion,u = read_input_file(input_file)
        number_of_particles = len(x)
        indices, errors = instance.new_particle(x, y, z, n_H, flux, X_ion,u)
        instance.commit_particles()

        self.assertEqual(16384.,instance.get_box_size()['box_size'])
        self.assertEqual(1,instance.get_hilbert_order()['hilbert_order'])
        self.assertEqual(0.5,instance.get_timestep()['timestep'])

        self.assertEqual(0, instance.cleanup_code())
        instance.stop()
    

class TestSimpleX(TestWithMPI):

    def test1(self):
        print "Test 1: initialization"
        instance = SimpleX(**default_options)
        instance.initialize_code()
        instance.commit_parameters()
        instance.cleanup_code()
        instance.stop()
    
    def test2(self):
        print "Test 2: commit_particles, getters and setters"
        instance = SimpleX(**default_options)
        instance.initialize_code()
        instance.commit_parameters()
        
        input_file = os.path.join(instance.data_directory, 'vertices_test3.txt')
        particles = particles_from_input_file(input_file)
        instance.particles.add_particles(particles)
        instance.commit_particles()
#        for attribute in ['position', 'rho', 'flux', 'xion']:
#            self.assertAlmostEqual(13200.*getattr(particles, attribute),
#                                   13200.*getattr(instance.particles, attribute), 5)
#            setattr(instance.particles, attribute, getattr(particles, attribute)/2.0)
#            self.assertAlmostEqual(13200.*getattr(particles, attribute)/2.0,
#                                   13200.*getattr(instance.particles, attribute), 5)
        instance.cleanup_code()
        instance.stop()
    
    def test3(self):
        print "Test 3: evolve"
        instance = SimpleX(**default_options)
        instance.initialize_code()
        instance.commit_parameters()
        
        input_file = os.path.join(instance.data_directory, 'vertices_test3.txt')
        particles = particles_from_input_file(input_file)
        particles.du_dt = particles.u/(10|units.Myr)
        instance.particles.add_particles(particles)
#        instance.particles.du_dt=particles.du_dt
#        instance.commit_particles()
        instance.particles.du_dt=particles.du_dt
        self.assertAlmostEqual(instance.particles.xion.mean(), 0.0 | units.none)
        self.assertAlmostEqual(instance.particles.du_dt.mean().in_(units.cm**2/units.s**3),particles.du_dt.mean().in_(units.cm**2/units.s**3))
        instance.evolve_model(0.5 | units.Myr)
        self.assertAlmostEqual(instance.particles.du_dt.mean().in_(units.cm**2/units.s**3),particles.du_dt.mean().in_(units.cm**2/units.s**3))
        self.assertAlmostEqual(instance.particles.xion.mean(), 0.000930585139546 | units.none)
        instance.cleanup_code()
        instance.stop()

    def test4(self):
        print "Test 4: default parameters"
        instance = SimpleX(**default_options)
        default=dict( timestep= 0.05| units.Myr, 
                  source_effective_T=  1.e5 | units.K,
                  hilbert_order= 1 | units.none,
                  number_of_freq_bins= 1 | units.none,
                  thermal_evolution_flag = 0 | units.none,
                  blackbody_spectrum_flag = 0 | units.none,
                  box_size=13200 | units.parsec,
                  metal_cooling_flag=0 | units.none,
                  collisional_ionization_flag=0 | units.none)
        for x in default:
            self.assertEqual(getattr(instance.parameters,x), default[x])
        instance.commit_parameters()
        for x in default:
            self.assertEqual(getattr(instance.parameters,x), default[x])


    def test5(self):
        print "Test 4: default parameters"
        instance = SimpleX(**default_options)
        param=dict( timestep= 0.1| units.Myr, 
                  source_effective_T=  2.e5 | units.K,
                  hilbert_order= 3 | units.none,
                  number_of_freq_bins= 4 | units.none,
                  thermal_evolution_flag = 1 | units.none,
                  blackbody_spectrum_flag = 1 | units.none,
                  box_size=32100 | units.parsec,
                  metal_cooling_flag=1 | units.none,
                  collisional_ionization_flag=1 | units.none)
        for x in param:
            setattr(instance.parameters,x, param[x])
        for x in param:
            self.assertEqual(getattr(instance.parameters,x), param[x])


    
def read_input_file(input_file):
    file = open(input_file, 'r')
    lines = file.readlines()
    lines.pop(0)
    x, y, z, nh, flux, xion,u = [], [], [], [], [], [],[]
    for line in lines:
        l = line.strip().split()
        if len(l) >= 7:
            x.append(float(l[1]))
            y.append(float(l[2]))
            z.append(float(l[3]))
            nh.append(float(l[4]))
            flux.append(float(l[5]))
            xion.append(float(l[6]))
            u.append(float(l[7]))
            
    return x, y, z, nh, flux, xion,u

def particles_from_input_file(input_file):
    x, y, z, n_H, flux, X_ion,u = read_input_file(input_file)
    particles = Particles(len(x))
    particles.x = x | units.parsec
    particles.y = y | units.parsec
    particles.z = z | units.parsec
    particles.rho = n_H | units.amu / units.cm**3
    particles.flux = flux | 1.0e48 / units.s
    particles.xion = X_ion | units.none
    particles.u = u | (units.cm**2/units.s**2)
    return particles

import math        

class sim_job:

    def __init__(self, job_json):

        self.job_json = job_json
        self.job_id = job_json["job_id"]

        # gpu performance modeling with DVFS
        self.D = job_json["D"]
        self.delta = job_json["delta"]
        self.t0 = job_json["t0"]

        # gpu power modeling with DVFS
        self.gamma = job_json["gamma"]
        self.cg = job_json["cg"]
        self.power_basic = job_json["power_basic"]
        self.p_star = self.power_basic + self.gamma + self.cg
        self.p_hat = self.p_star

        # job metrics
        self.arrival = job_json["arrival"]
        self.t_star = self.t0 + self.D
        self.t_hat = self.t_star
        self.util = job_json["utilization"]
        self.deadline = self.arrival + self.t_star / self.util
    
        self.e_star = self.p_star * self.t_star
        self.e_min = self.e_star
        #self.solve_dvfs()

        self.is_finished = False

        self.node = -1
        self.gpu = -1

        self.finish_time = 0

    def solve_dvfs(self):

        self.fc = 1
        self.fm = 1
        self.v = 1
        self.e_min = self.e_star
        for v_adj in range(0, 16):
            v = 0.5 + 0.05 * v_adj
            fc = math.sqrt((v - 0.5) / 2.0) + 0.5
            fm = math.sqrt((self.power_basic+self.cg*(v**2)*fc)*self.D*(1-self.delta) / (self.gamma * (self.t0 + self.D*self.delta/fc)))
            #print "calculate fmem: %f." % fm
            if fm <= 0.5:
               fm = 0.5
            if fm >= 1.2:
               fm = 1.2

            t_cur = self.t0 + self.D * (self.delta / fc + (1 - self.delta) / fm)
            p_cur = self.power_basic + self.gamma * fm + self.cg * (v**2) * fc
            e_cur = t_cur * p_cur

            if self.arrival + t_cur > self.deadline:
                continue
            if e_cur < self.e_min:
                self.e_min = e_cur
                self.v = v
                self.fc = fc
                self.fm = fm
                self.t_hat = t_cur
                self.p_hat = p_cur
        print "job %d: v_core: %f, f_core: %f, f_mem: %f, p: %f, t: %f, saving: %f." % (self.job_id, self.v, self.fc, self.fm, self.p_hat, self.t_hat, (self.e_star - self.e_min) / self.e_star)            
    def get_dvfs_time(self):
        return self.t_hat

    def get_dvfs_power(self):
        return self.p_hat

    def set_node(self, node):
        self.node = node

    def get_node(self):
        return self.node

    def set_gpu(self, gpu):
        self.gpu = gpu
                
    def set_finish_time(self, end_time):
        self.finish_time = end_time


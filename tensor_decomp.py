import datetime
import numpy as np
import os
import tensorflow as tf
import time

class CPDecomp(object):
    def __init__(self, shape, rank, sess, ndims=3, optimizer_type='adam', reg_param=1e-10, is_glove=False, nonneg=False):
        '''
        `rank` is R, the number of 1D tensors to hold to get an approximation to `X`
        `optimizer_type` must be in ('adam', 'sgd', 'sals', '2sgd', 'adagrad')
        
        Approximates a tensor whose approximations are repeatedly fed in batch format to `self.train`
        '''
        self.rank = rank
        self.optimizer_type = optimizer_type
        self.shape = shape
        self.ndims = ndims
        self.sess = sess
        self.is_glove = is_glove
        self.nonneg = nonneg

        with tf.device('/cpu:0'):
            # t-th batch tensor
            # contains all data for this minibatch. already summed/averaged/whatever it needs to be. 
            self.indices = tf.placeholder(tf.int64, shape=[None, self.ndims], name='X_t_indices')
            self.values = tf.placeholder(tf.float32, shape=[None], name='X_t_values')
            shape_sparse = np.array(self.shape, dtype=np.int64)
            self.X_t = tf.SparseTensorValue(self.indices, self.values, dense_shape=shape_sparse)
            # Goal: X_ijk == sum_{r=1}^{R} U_{ir} V_{jr} W_{kr}
            self.U = tf.Variable(tf.random_uniform(
                shape=[self.shape[0], self.rank],
                minval=-1.0,
                maxval=1.0,
            ), name="U")
            if self.nonneg:
                self.U = tf.nn.relu(self.U)
            self.V = tf.Variable(tf.random_uniform(
                shape=[self.shape[1], self.rank],
                minval=-1.0,
                maxval=1.0,
            ), name="V")
            if self.ndims > 2:
                self.W = tf.Variable(tf.random_uniform(
                    shape=[self.shape[2], self.rank],
                    minval=-1.0,
                    maxval=1.0,
                ), name="W")
            self.create_loss_fn(reg_param=reg_param)

    def train_step(self, approx_indices, approx_values, print_every=1):
        if not hasattr(self, 'prev_time'):
            self.prev_time = time.time()
            self.avg_time = 0.0
            self.total_recordings = 0
        feed_dict = {
            self.indices: approx_indices,
            self.values: approx_values,
        }
        t = time.time()
        _, step, *debug_tensies = self.sess.run(
            [
                self.train_ops, # might need multiple train ops to be executed sequentially (see the case of sals)
                self.global_step,
            ],
            feed_dict=feed_dict,
        )
        if step % print_every == 0:
            print('step {} took {} secs'.format(step, time.time() - t))
        if self.checkpoint_every is not None:
            if step % self.checkpoint_every == 0 and step > 0:
                t = time.time()
                print('Saving checkpoint at step {}...'.format(step))
                path = self.saver.save(self.sess, self.checkpoint_prefix, global_step=self.global_step)
                print('Saved model checkpoint to {} (it took {} secs)'.format(path, time.time() - t))

        if step % print_every == 0:
            t = time.time()
            err = self.sess.run(
                [
                    self.L,
                ],
                feed_dict=feed_dict,
            )
            #print('getting loss took {} secs'.format(time.time() - t))

            batch_time = (time.time() - self.prev_time) / print_every
            print("Err at step {}: {}; (avg batch time: {})".format(step, err, batch_time))
            self.prev_time = time.time()
            self.avg_time = (batch_time + self.total_recordings * self.avg_time) / (self.total_recordings + 1.0)
            self.total_recordings += 1
        
    def create_loss_fn(self, reg_param):
        """
        L(X; U,V,W) = .5 sum_{i,j,k where X_ijk =/= 0} (X_ijk - sum_{r=1}^{R} U_ir V_jr W_kr)^2
        L_{rho} = L(X; U,V,W) + rho * (||U||^2 + ||V||^2 + ||W||^2) where ||.|| represents some norm (L2, L1, Frobenius)
        """
        def L(X):
            """
            X is a sparse tensor. U,V,W are dense. 
            """
            if self.ndims > 2:
                raise NotImplementedError  # TODO: re-fix if need higher dims
                predict_val_fn = lambda x: tf.reduce_sum(tf.gather(self.U, x[0]) * tf.gather(self.V, x[1]) * tf.gather(self.W, x[2]))
            else:
                if self.ndims == 2:
                    vects_1 = tf.nn.embedding_lookup(self.U, tf.gather(tf.transpose(X.indices), 0))
                    vects_2 = tf.nn.embedding_lookup(self.V, tf.gather(tf.transpose(X.indices), 1))
                    prods = vects_1 * vects_2
                    dots = tf.reduce_sum(prods, axis=1)
                    if self.is_glove:
                        B1s = tf.Variable(tf.random_uniform(
                            shape=[self.shape[0], 1],
                            minval=-1.0,
                            maxval=1.0,
                        ), name="b1s")
                        B2s = tf.Variable(tf.random_uniform(
                            shape=[self.shape[0], 1],
                            minval=-1.0,
                            maxval=1.0,
                        ), name="b2s")
                        predicted_vals = dots + tf.nn.embedding_lookup(B1s, tf.gather(tf.transpose(X.indices), 0)) \
                                      + tf.nn.embedding_lookup(B2s, tf.gather(tf.transpose(X.indices), 1))
                    else:
                        predicted_vals = dots
                    errs = tf.squared_difference(predicted_vals, X.values)
                    if self.is_glove:
                        errs = errs * tf.minimum(1., ((tf.exp(X.values)) / 100.) ** 0.75)  # X.values[i] is log(X_ij)
            return tf.reduce_mean(errs)

        def reg():
            # NOTE: l2_loss already squares the norms. So we don't need to square them.
            summed_norms = (
                tf.nn.l2_loss(self.U, name="U_norm") +
                tf.nn.l2_loss(self.V, name="V_norm") +
                tf.nn.l2_loss(self.W, name="W_norm")
            )
            return (.5 * reg_param) * summed_norms

        self.L = L(self.X_t)
        self.reg = tf.constant(0.0)
        if reg_param > 0.0 and self.ndims > 2:
            self.reg = reg(self.U, self.V, self.W)
        else:
            if not self.is_glove:
                self.reg = reg_param * tf.norm(self.U, ord=1)
        self.loss = self.L + self.reg

        
    def get_train_ops(self):
        if self.optimizer_type == '2sgd':
            train_ops = [self.get_train_op_2sgd()]
        elif self.optimizer_type == 'sals':
            train_ops = self.get_train_ops_sals()
        elif self.optimizer_type == 'adam':
            train_ops = [self.get_train_op_adam()]
        elif self.optimizer_type == 'sgd':
            train_ops = [self.get_train_op_sgd()]
        elif self.optimizer_type == 'adagrad':
            train_ops = [self.get_train_op_adagrad()]
        inc_t = tf.assign(self.global_step, self.global_step+1)
        return [*train_ops, inc_t]

    def get_update_UVW_ops_for_2sgd_sals(self, rho):
        '''
        See 2SGD/SALS algorithms in Expected Tensor Decomp paper
        '''
        def gamma(A,B):
            ATA = tf.matmul(A,A, transpose_a=True)  # A^T * A
            BTB = tf.matmul(B,B, transpose_a=True)  # B^T * B
            return tf.multiply(ATA, BTB)  # hadamard product of A^T*A and B^T*B

        X = self.X_t
        t = self.global_step + 1
        alpha = .25  # smaller => decays slower (more quickly get updates from the gradients)
        #batch_size = 1. / 500. * tf.sqrt(tf.cast(X.shape[0], tf.float32))
        batch_size = 1.
        eta_t = batch_size / (1. + t**alpha)

        X_VW = tf.Variable(tf.constant(0.0, shape=[self.shape[0], self.rank]))
        XU_W = tf.Variable(tf.constant(0.0, shape=[self.shape[1], self.rank]))
        XUV_ = tf.Variable(tf.constant(0.0, shape=[self.shape[2], self.rank]))

        def assign_zeroes():
            a1 = tf.assign(X_VW, tf.constant(0.0, shape=[self.shape[0], self.rank]))
            a2 = tf.assign(XU_W, tf.constant(0.0, shape=[self.shape[1], self.rank]))
            a3 = tf.assign(XUV_, tf.constant(0.0, shape=[self.shape[2], self.rank]))
            return tf.group(a1, a2, a3)

        def body(ix, X_VW2,XU_W2,XUV_2,):
            ijk = tf.gather(X.indices, ix)
            val = tf.gather(X.values, ix)
            Ui = tf.gather(self.U, ijk[0])  # R-dimensional
            Vj = tf.gather(self.V, ijk[1])
            Wk = tf.gather(self.W, ijk[2])

            Xijk_Vj_Wk = val * tf.multiply(Vj, Wk) 
            Xijk_Ui_Wk = val * tf.multiply(Ui, Wk) 
            Xijk_Ui_Vj = val * tf.multiply(Ui, Vj) 

            r1 = tf.scatter_add(X_VW, ijk[0], Xijk_Vj_Wk)  # add Xijk(Vj*Wk) to X_VW(i,:) (as vectors in \mathbb{R}^R)
            r2 = tf.scatter_add(XU_W, ijk[1], Xijk_Ui_Wk)
            r3 = tf.scatter_add(XUV_, ijk[2], Xijk_Ui_Vj)
            new_ix = tf.add(ix, tf.constant(1))
            return new_ix, r1, r2, r3

        N = tf.shape(X.values)[0]
        def cond(ix, *args):
            ass = tf.cond(tf.equal(ix, tf.constant(0)), lambda: assign_zeroes(), lambda: tf.no_op())
            with tf.control_dependencies([ass]):
                return tf.less(ix, N)

        printer = tf.Print(XUV_, [X_VW, XU_W, XUV_])
        ix = tf.Variable(tf.constant(0, dtype=tf.int32))  # which index/value we're looking at
        _, X_VW, XU_W, XUV_ = tf.while_loop(cond, body, [ix, X_VW, XU_W, XUV_])

        U = self.U
        V = self.V
        W = self.W

        self.D1 = X_VW
        self.D2 = XU_W
        self.D3 = XUV_

        gamma_rho = gamma(V,W) + rho * tf.eye(self.rank)
        self.gr1 = gamma_rho
        inv_gamma_rho = tf.matrix_inverse(gamma_rho)
        self.gr1inv = gamma_rho
        self.grad_value_U = tf.matmul(X_VW, inv_gamma_rho)

        gamma_rho = gamma(U,W) + rho * tf.eye(self.rank)
        self.gr2 = gamma_rho
        inv_gamma_rho = tf.matrix_inverse(gamma_rho)
        self.grad_value_V = tf.matmul(XU_W, inv_gamma_rho)

        gamma_rho = gamma(U,V) + rho * tf.eye(self.rank)
        self.gr3 = gamma_rho
        inv_gamma_rho = tf.matrix_inverse(gamma_rho)
        self.grad_value_W = tf.matmul(XUV_, inv_gamma_rho)

        update_U_op = tf.assign(U, (1-eta_t) * U + eta_t * self.grad_value_U)
        update_V_op = tf.assign(V, (1-eta_t) * V + eta_t * self.grad_value_V)
        update_W_op = tf.assign(W, (1-eta_t) * W + eta_t * self.grad_value_W)
        return [update_U_op, update_V_op, update_W_op]

    def get_train_op_2sgd(self, rho=1e-3):
        [update_U_op, update_V_op, update_W_op] = self.get_update_UVW_ops_for_2sgd_sals(rho)
        # Update U,V,W simultaneously - I believe tf.group does this?
        update_CP_op = tf.group(update_U_op, update_V_op, update_W_op)
        return update_CP_op

    def get_train_ops_sals(self, rho=1e-3):
        [update_U_op, update_V_op, update_W_op] = self.get_update_UVW_ops_for_2sgd_sals(rho)
        # update U,V,W in order
        return [update_U_op, update_V_op, update_W_op]

    def get_train_op_adam(self):
        return self.optimizer.minimize(self.loss)

    def get_train_op_sgd(self):
        return self.optimizer.minimize(self.loss)

    def get_train_op_adagrad(self):
        return self.optimizer.minimize(self.loss)

    def train(self, expected_tensors, true_X=None, evaluate_every=100, results_file=None, write_loss=True, checkpoint_every=None):
        '''
        Assumes `expected_tensors` is a generator of sparse tensor values. 
        '''
        self.batch_num = 0
        self.results_file = results_file
        num_invalid_arg_exceptions = 0
        with tf.device('/cpu:0'):
            print('setting up variables...')
            self.global_step = tf.Variable(0.0, name='global_step', trainable=False)
            if self.optimizer_type == 'adam':
                self.optimizer = tf.train.AdamOptimizer(learning_rate=1e-3)
            elif self.optimizer_type == 'sgd':
                self.optimizer = tf.train.GradientDescentOptimizer(learning_rate=1e-0)
            elif self.optimizer_type == 'adagrad':
                self.optimizer = tf.train.AdagradOptimizer(learning_rate=.05)

            self.train_ops = self.get_train_ops()

        self.write_loss = write_loss
        if self.write_loss:
            timestamp = str(datetime.datetime.now())
            out_dir = os.path.abspath(os.path.join(os.path.curdir, 'tf_logs', timestamp))
            print('Writing summaries to {}.'.format(out_dir))
            self.loss_summary = tf.summary.scalar('loss', self.loss)
            self.train_summary_writer = tf.summary.FileWriter(os.path.join(out_dir, 'summaries'), self.sess.graph)
        else:
            self.loss_summary = self.global_step  # so it doesnt crash when i try to evaluate loss_summary

        self.checkpoint_every = checkpoint_every
        if self.checkpoint_every is not None:
            checkpoint_dir = os.path.abspath(os.path.join(out_dir, 'checkpoints'))
            self.checkpoint_prefix = os.path.join(checkpoint_dir, 'model')

            if not os.path.exists(checkpoint_dir):
                os.makedirs(checkpoint_dir)
            self.saver = tf.train.Saver(tf.global_variables(), write_version=tf.train.SaverDef.V2)

        print('initializing variables...')
        self.sess.run(tf.global_variables_initializer())
        print("Starting ASYMMETRIC CP Decomp training")
        #print("U: {}".format(self.U.eval(self.sess)))
        with self.sess.as_default():
            print('looping through batches...')
            for expected_indices, expected_values in expected_tensors:
                try:
                    self.train_step(expected_indices, expected_values, print_every=100)
                except tf.errors.InvalidArgumentError as e:
                    self.batch_num -= 1
                    num_invalid_arg_exceptions += 1
                    print("INVALID ARG EXCEPTION: {}. Accidentally noninvertible matrix? There have been {} of these.".format(e, num_invalid_arg_exceptions))
                    import pdb; pdb.set_trace()
                self.batch_num += 1
            if hasattr(self, 'avg_time') and results_file is not None:
                print('avg batch time: {}'.format(self.avg_time), file=results_file)
        if self.write_loss:
            self.train_summary_writer.close()
        if self.checkpoint_every is not None:
            print('saving final checkpoint...')
            path = self.saver.save(self.sess, self.checkpoint_prefix, global_step=self.global_step)


def test_decomp():
    shape = [3, 40, 50]
    true_U = np.random.rand(shape[0], 5)
    true_V = np.random.rand(shape[1], 5)
    true_W = np.random.rand(shape[2], 5)
    true_X = np.einsum('ir,jr,kr->ijk', true_U, true_V, true_W)

    def batch_tensors_gen(n):
        for _ in range(n):
            yield true_X + (np.random.rand(*tuple(shape)) - 0.5) 

    def sparse_batch_tensor_generator(n=1500):
        import random
        with tf.device('/cpu:0'):
            for X_t in batch_tensors_gen(n):
                indices = []
                values = []
                for i in range(shape[0]):
                    for j in range(shape[1]):
                        for k in range(shape[2]):
                            if random.random() >= 0.0:
                                indices.append([i,j,k])
                                values.append(X_t[i,j,k])
                indices = np.asarray(indices)
                values = np.asarray(values)
                print('{} nonzero vals'.format(len(indices)))
                yield (indices, values)

    config = tf.ConfigProto(
        allow_soft_placement=True,
    )
    sess = tf.Session(config=config)
    print('training (on 2sgd)!')
    with open('results_2sgd.txt', 'w') as f:
        # train 2sgd
        decomp_method = CPDecomp(
            shape=shape,
            sess=sess,
            rank=300,
            ndims=3,
            optimizer_type='2sgd',
        )
        decomp_method.train(sparse_batch_tensor_generator(), true_X=None, evaluate_every=2, results_file=f, write_loss=False)


class SymmetricCPDecomp(object):
    def __init__(self, dim, rank, sess, ndims=3, optimizer_type='adam', reg_param=1e-10, nonneg=True, gpu=True, is_glove=False, mean_value=None):
        '''
        `rank` is R, the number of 1D tensors to hold to get an approximation to `X`
        since X is supersymmetric, `dim` is the length of each dimension
        
        Approximates a supersymmetric tensor whose approximations are repeatedly fed in batch format (indices always in sorted order) to `self.train`
        '''
        self.rank = rank
        self.optimizer_type = optimizer_type
        self.shape = [dim] * ndims
        self.ndims = ndims
        self.sess = sess
        self.nonneg = nonneg
        self.reg_param = reg_param
        self.gpu = gpu
        self.mean_value = mean_value
        self.is_glove = is_glove

        with tf.device('/{}:0'.format('gpu' if self.gpu else 'cpu')):
            # t-th batch tensor
            self.indices = tf.placeholder(tf.int64, shape=[None, self.ndims], name='X_t_indices')  # always fed in in a sorted way
            self.values = tf.placeholder(tf.float32, shape=[None], name='X_t_values')
            shape_sparse = np.array(self.shape, dtype=np.int64)
            
            self.X_t = tf.SparseTensorValue(self.indices, self.values, dense_shape=shape_sparse)
            # Goal: X_ijk == sum_{r=1}^{R} U_{ir} U_{jr} U_{kr}
            if self.mean_value is None:
                mu = 10.0
            else:
                mu = self.mean_value
            mean = ((1. / self.rank) * mu) ** (1/self.ndims)
            self.U = tf.Variable(tf.random_normal(
                shape=[dim, self.rank],
                mean=mean,
                stddev=mean / 5,
            ), name="U")
            if self.nonneg:
                self.sparse_U = tf.nn.relu(self.U, name='Sparse_U')
        self.create_loss_fn(reg_param=reg_param)

    def train_step(self, approx_tensor, print_every=10, validate_indices=False):
        approx_indices, approx_values = approx_tensor
        if not hasattr(self, 'prev_time'):
            self.prev_time = time.time()
            self.avg_time = 0.0
        feed_dict = {
            self.indices: approx_indices,
            self.values: approx_values,
        }
        if validate_indices:
            for ix in approx_indices:
                assert ((sorted(ix) - ix) == 0).all(), 'Indices must be fed in only in sorted order. offending ix: {}'.format(ix)
        _, loss_summary, step = self.sess.run(
            [
                self.train_ops,
                self.loss_summary,
                self.global_step,
            ],
            feed_dict=feed_dict,
        )
        if self.write_loss:
            self.train_summary_writer.add_summary(loss_summary, step)
        if self.checkpoint_every is not None:
            if step % self.checkpoint_every == 0 and step > 0:
                t = time.time()
                print('Saving checkpoint at step {}...'.format(step))
                path = self.saver.save(self.sess, self.checkpoint_prefix, global_step=self.global_step)
                print('Saved model checkpoint to {} (it took {} secs)'.format(path, time.time() - t))

        if step % print_every == 0:
            t = time.time()
            err, reg = self.sess.run(
                [
                    self.L,
                    self.reg,
                ],
                feed_dict=feed_dict,
            )
            batch_time = (time.time() - self.prev_time) / print_every
            print("Err at step {}: {:.3f}; Reg loss: {:.3f} (lambda = {:.1E}) (Avg batch time: {:.3f})".format(int(step), err, reg, self.reg_param, batch_time))
            self.prev_time = time.time()
        
    def create_loss_fn(self, reg_param):
        """
        L(X; U) = .5 sum_{i,j,k where X_ijk =/= 0} (X_ijk - sum_{r=1}^{R} U_ir U_jr U_kr)^2
        L_{rho} = L(X; U) + rho * (||U||^2) where ||.|| represents some norm (L2, L1, Frobenius)
        """
        def L(X, U):
            """
            X is a sparse tensor. U is dense. 
            """
            indices = tf.transpose(X.indices)  # of shape (N,3) - represents the indices of all values (in the same order as X.values)
            with tf.device('/{}'.format('gpu:1' if self.gpu else 'cpu:0')):
                X_ijks = X.values  # of shape (N,) - represents all the values stored in X. 

                prod_vects = tf.gather(U, tf.gather(indices, 0, name='0_indices'), name='0_vects')
                for i in range(1, self.ndims):
                    i_indices = tf.gather(indices, i, name='{}_indices'.format(i))  # of shape (N,) - represents all the indices to get from the U matrix
                    i_vects = tf.gather(U, i_indices, name='{}_vects'.format(i))
                    prod_vects *= i_vects
                    predicted_X_ijks = tf.reduce_sum(prod_vects, axis=1)
               
                if self.is_glove:
                    B1s = tf.Variable(tf.random_uniform(
                        shape=[self.shape[0], 1],
                        minval=-1.0,
                        maxval=1.0,
                    ), name="b1s")
                    B2s = tf.Variable(tf.random_uniform(
                        shape=[self.shape[0], 1],
                        minval=-1.0,
                        maxval=1.0,
                    ), name="b2s")
                    predicted_X_ijks = predicted_X_ijks + tf.nn.embedding_lookup(B1s, tf.gather(tf.transpose(X.indices), 0)) \
                                  + tf.nn.embedding_lookup(B2s, tf.gather(tf.transpose(X.indices), 1))
                errors = tf.squared_difference(X_ijks, predicted_X_ijks)  # of shape (N,) - elementwise error for each entry in X_ijk
                if self.is_glove:
                    errors = errors * tf.minimum(1., ((tf.exp(X_ijks)) / 100.) ** 0.75)  # X.values[i] is log(X_ij)
                mean_loss = tf.reduce_mean(errors)  # average loss per entry in X - scalar!
                return mean_loss

        def reg(U):
            with tf.device('/{}'.format('gpu:1' if self.gpu else 'cpu:0')):
                if self.nonneg:
                    return reg_param * tf.reduce_sum(tf.abs(U))
                else:
                    # NOTE: l2_loss already squares the norms. So we don't need to square them.
                    return .5  * reg_param * tf.nn.l2_loss(U, name="U_L2_norm")

        U = self.U
        if self.nonneg:
            U = self.sparse_U
        self.L = L(self.X_t, U)
        if reg_param > 0.0:
            self.reg = reg(U) 
        else:
            self.reg = tf.constant(0.0)
        self.loss = self.L + self.reg
        
    def get_train_ops(self):
        train_ops = [self.get_train_op_adam()]
        inc_t = tf.assign(self.global_step, self.global_step+1)
        return [*train_ops, inc_t]

    def get_train_op_adam(self):
        return self.optimizer.minimize(self.loss)

    def train(self, expected_tensors, results_file=None, write_loss=True, checkpoint_every=None):
        '''
        Assumes `expected_tensors` is a generator of sparse tensor values. 
        '''
        self.batch_num = 0
        self.results_file = results_file
        num_invalid_arg_exceptions = 0
        with tf.device('/{}'.format('gpu:0' if self.gpu else 'cpu:0')):
            print('setting up variables...')
            self.global_step = tf.Variable(0.0, name='global_step', trainable=False)
            self.optimizer = tf.train.AdamOptimizer(learning_rate=.001)

            self.train_ops = self.get_train_ops()

        self.write_loss = write_loss
        if self.write_loss:
            timestamp = str(datetime.datetime.now())
            out_dir = os.path.abspath(os.path.join(os.path.curdir, 'tf_logs', timestamp))
            print('Writing summaries to {}.'.format(out_dir))
            self.loss_summary = tf.summary.scalar('loss', self.loss)
            self.train_summary_writer = tf.summary.FileWriter(os.path.join(out_dir, 'summaries'), self.sess.graph)
        else:
            self.loss_summary = self.global_step  # so it doesnt crash when i try to evaluate loss_summary

        self.checkpoint_every = checkpoint_every
        if self.checkpoint_every is not None:
            checkpoint_dir = os.path.abspath(os.path.join(out_dir, 'checkpoints'))
            self.checkpoint_prefix = os.path.join(checkpoint_dir, 'model')

            if not os.path.exists(checkpoint_dir):
                os.makedirs(checkpoint_dir)
            self.saver = tf.train.Saver(tf.global_variables(), write_version=tf.train.SaverDef.V2)

        print('initializing variables...')
        self.sess.run(tf.global_variables_initializer())
        with self.sess.as_default():
            print('looping through batches...')
            for expected_tensor in expected_tensors:
                try:
                    self.train_step(expected_tensor)
                except tf.errors.InvalidArgumentError as e:
                    self.batch_num -= 1
                    num_invalid_arg_exceptions += 1
                    print("INVALID ARG EXCEPTION: {}. Accidentally noninvertible matrix? There have been {} of these.".format(e, num_invalid_arg_exceptions))
                    import pdb; pdb.set_trace()
                self.batch_num += 1
            if self.checkpoint_every is not None:
                try:
                    path = self.saver.save(self.sess, checkpoint_dir, global_step=tf.train.global_step(self.sess, self.global_step))
                    print('Saved FINAL model checkpoint to {}'.format(path))
                except Exception as e:
                    print(e)
                    print("Caught exception trying to checkpoint the final model. You're welcome ;)")
                    import pdb; pdb.set_trace()
                    pass
        if self.write_loss:
            self.train_summary_writer.close()


class JointSymmetricCPDecomp(SymmetricCPDecomp):
    def __init__(self, size, rank, sess, dimlist=[2,3], dimweights=[1., 1.], reg_param=1e-10, nonneg=True, gpu=True):
        '''
        `rank` is R, the number of 1D tensors to hold to get an approximation to `X`
        since X is supersymmetric, `size` is the length of each dimension
        
        Approximates a supersymmetric tensor whose approximations are repeatedly fed in batch format (indices always in sorted order) to `self.train`
        '''
        self.dimlist = dimlist
        self.dimweights = dimweights
        assert len(dimlist) == len(dimweights)
        self.rank = rank
        self.sess = sess
        self.nonneg = nonneg
        self.reg_param = reg_param
        self.gpu = gpu

        self.indices = []
        self.values = []
        self.X_ts = []
        with tf.device('/{}:0'.format('gpu' if self.gpu else 'cpu')):
            # t-th batch tensor
            for dim in dimlist:
                indices = tf.placeholder(tf.int64, shape=[None, dim], name='X_t_indices_{}'.format(dim))
                values = tf.placeholder(tf.float32, shape=[None], name='X_t_values_{}'.format(dim))
                self.indices.append(indices)
                self.values.append(values)
                shape_sparse = np.array([size] * dim, dtype=np.int64)
                self.X_ts.append(tf.SparseTensorValue(indices, values, dense_shape=shape_sparse))
            # Goal: X_ijk == sum_{r=1}^{R} U_{ir} U_{jr} U_{kr}
            mu = 15.0
            mean = ((1. / self.rank) * mu) ** (1/2)
            self.U = tf.Variable(tf.random_normal(
                shape=[size, self.rank],
                mean=mean,
                stddev=mean / 5,
            ), name="U")
            print('nonneg: {}'.format(self.nonneg))
            if self.nonneg:
                self.sparse_U = tf.nn.relu(self.U, name='Sparse_U')
        self.create_loss_fn(reg_param=reg_param)

    def train_step(self, approx_tensor, print_every=10):
        approx_indices, approx_values = approx_tensor
        if not hasattr(self, 'prev_time'):
            self.prev_time = time.time()
            self.avg_time = 0.0
            self.total_recordings = 0

        feed_dict = {}
        for ixes, vals, i in zip(approx_indices, approx_values, range(len(self.dimlist))):
            feed_dict[self.indices[i]] = ixes
            feed_dict[self.values[i]] = vals
        _, loss_summary, step = self.sess.run(
            [
                self.train_ops,
                self.loss_summary,
                self.global_step,
            ],
            feed_dict=feed_dict,
        )
        if self.checkpoint_every is not None:
            if step % self.checkpoint_every == 0 and step > 0:
                t = time.time()
                print('Saving checkpoint at step {}...'.format(step))
                path = self.saver.save(self.sess, self.checkpoint_prefix, global_step=self.global_step)
                print('Saved model checkpoint to {} (it took {} secs)'.format(path, time.time() - t))

        if step % print_every == 0:
            t = time.time()
            errs, reg = self.sess.run(
                [
                    self.Ls,
                    self.reg,
                ],
                feed_dict=feed_dict,
            )
            batch_time = (time.time() - self.prev_time) / print_every
            # string formatting to print the errors for each dimension
            errstring = '; '.join(['{}d: {:.2f}'.format(dim, err) for dim, err in zip(self.dimlist, errs)])
            print("{}: Errs: {}; Reg loss: {:.2f} (lambda={:.1E}) (Avg time: {:.2f})".format(int(step), errstring, reg, self.reg_param, batch_time))
            self.prev_time = time.time()
            self.total_recordings += 1
        
    def create_loss_fn(self, reg_param):
        """
        L(X; U) = .5 sum_{i,j,k where X_ijk =/= 0} (X_ijk - sum_{r=1}^{R} U_ir U_jr U_kr)^2
        L_{rho} = L(X; U) + rho * (||U||^2) where ||.|| represents some norm (L2, L1, Frobenius)
        """
        def L(X, U, dim):
            """
            X is a sparse tensor. U is dense. 
            """
            indices = tf.transpose(X.indices)  # of shape (N,3) - represents the indices of all values (in the same order as X.values)
            with tf.device('/{}'.format('gpu:1' if self.gpu else 'cpu:0')):
                X_ijks = X.values  # of shape (N,) - represents all the values stored in X. 

                prod_vects = tf.gather(U, tf.gather(indices, 0))
                for i in range(1, dim):
                    i_indices = tf.gather(indices, i)  # of shape (N,) - represents all the indices to get from the U matrix
                    i_vects = tf.gather(U, i_indices)
                    prod_vects *= i_vects
                predicted_X_ijks = tf.reduce_sum(prod_vects, axis=1)
               
                errors = tf.squared_difference(X_ijks, predicted_X_ijks)  # of shape (N,) - elementwise error for each entry in X_ijk
                mean_loss = tf.reduce_mean(errors)  # average loss per entry in X - scalar!
                return mean_loss

        def reg(U):
            with tf.device('/{}'.format('gpu:1' if self.gpu else 'cpu:0')):
                if self.nonneg:
                    return reg_param * tf.reduce_sum(tf.abs(U))
                else:
                    # NOTE: l2_loss already squares the norms. So we don't need to square them.
                    return .5  * reg_param * tf.nn.l2_loss(U, name="U_L2_norm")

        U = self.U
        if self.nonneg:
            U = self.sparse_U
        if reg_param > 0.0:
            self.reg = reg(U) 
        else:
            self.reg = tf.constant(0.0)
        self.Ls = []
        for i, dim in enumerate(self.dimlist):
            self.Ls.append(self.dimweights[i] * L(self.X_ts[i], U, dim))
        self.L = sum(self.Ls)
        self.loss = self.L + self.reg


def test_symmetric_decomp():
    shape = [30, 30, 30]
    true_X = np.zeros(shape)
    indices = []
    vals = []
    print('filling tensor...')
    for i in range(30):
        for j in range(i+1, 30):
            for k in range(j+1, 30):
                val = np.random.rand()
                true_X[i][j][k] = val
                true_X[i][k][j] = val
                true_X[j][i][k] = val
                true_X[j][k][i] = val
                true_X[k][i][j] = val
                true_X[k][j][i] = val
                indices.append(np.array([i,j,k]))
                vals.append(val)
    indices = np.array(indices)
    vals = np.array(vals)

    def batch_tensors_gen(n):
        for _ in range(n):
            yield true_X + (np.random.rand(*tuple(shape)) - 0.5) 

    def sparse_batch_tensor_generator(indices, vals):
        import random
        for _ in range(5000):
            values = vals + np.random.rand(len(vals)) - 0.5
            yield (indices, values)

    config = tf.ConfigProto(
        allow_soft_placement=True,
    )
    sess = tf.Session(config=config)
    with open('results_adam.txt', 'w') as f:
        decomp_method = SymmetricCPDecomp(
            dim=shape[0],
            sess=sess,
            rank=100,
            ndims=3,
            optimizer_type='adam',
            reg_param=0.0,
        )
        decomp_method.train(sparse_batch_tensor_generator(indices, vals), results_file=f, write_loss=False)


def test_joint_decomp():
    shape = [30, 30, 30]

    indices2 = []
    indices3 = []
    vals = []
    print('filling tensor...')
    for i in range(30):
        for j in range(i+1, 30):
            for k in range(j+1, 30):
                val = np.random.rand()
                indices2.append(np.array([i,j]))
                indices3.append(np.array([i,j,k]))
                vals.append(val)
    indices2 = np.array(indices2)
    indices3 = np.array(indices3)
    vals = np.array(vals)

    def sparse_batch_tensor_generator(indices2, indices3, vals):
        import random
        for _ in range(5000):
            values = vals + np.random.rand(len(vals)) - 0.5
            yield ([indices2, indices3], [values, values])

    config = tf.ConfigProto(
        allow_soft_placement=True,
    )
    sess = tf.Session(config=config)
    with open('results_adam.txt', 'w') as f:
        decomp_method = JointSymmetricCPDecomp(
            size=30,
            dimlist=[2,3],
            sess=sess,
            rank=100,
            reg_param=0.000001,
        )
        decomp_method.train(sparse_batch_tensor_generator(indices2, indices3, vals), results_file=f, write_loss=False)


if __name__ == '__main__':
    print('testing CP decomp...')
    #test_decomp()
    #test_symmetric_decomp()
    test_joint_decomp()

